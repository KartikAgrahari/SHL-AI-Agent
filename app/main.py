from fastapi import FastAPI
from pydantic import BaseModel
from app.agent import (
    analyze_conversation,
    generate_reply
)
from app.retrieval import (
    load_catalog,
    create_embeddings,
    build_faiss_index,
    search_assessments
)

app = FastAPI()


# Load catalog
catalog = load_catalog()

# Create embeddings
embeddings = create_embeddings(catalog)

# Build FAISS index
index = build_faiss_index(embeddings)


@app.get("/health")
def health():

    return {"status": "ok"}


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]


@app.post("/chat")
def chat(request: ChatRequest):

    conversation_text = " ".join(
        [msg.content for msg in request.messages]
    ).lower()

    latest_user_message = request.messages[-1].content.lower()

    analysis = analyze_conversation(
        conversation_text
    )

    if analysis["status"] == "follow_up":

        return {
            "reply": analysis["question"],
            "recommendations": [],
            "end_of_conversation": False
        }
    

    # Follow-up clarification logic
    needs_clarification = False

    clarification_reply = ""


    if "developer" in latest_user_message:

        if (
            "java" not in conversation_text
            and "python" not in conversation_text
            and "frontend" not in conversation_text
            and "backend" not in conversation_text
        ):

            needs_clarification = True

            clarification_reply = (
                "Could you specify the type "
                "of developer role? "
                "For example: Java backend, "
                "frontend, Python, full stack, etc."
            )


    elif "manager" in latest_user_message:

        if (
            "project" not in conversation_text
            and "product" not in conversation_text
        ):

            needs_clarification = True

            clarification_reply = (
                "Could you specify whether "
                "this is for project management, "
                "product management, or another "
                "management role?"
            )


    if needs_clarification:

        return {
            "reply": clarification_reply,
            "recommendations": [],
            "end_of_conversation": False
        }


    # Retrieval
    results = search_assessments(
        conversation_text,
        catalog,
        index,
        top_k=5
    )

    # No results
    if not results:

        return {
            "reply": (
                "I could not find relevant SHL "
                "assessment recommendations "
                "for your request."
            ),
            "recommendations": [],
            "end_of_conversation": False
        }


    # Similarity confidence
    best_distance = results[0]["distance"]


    # Weak semantic match
    if best_distance > 1.2:

        return {
            "reply": (
                "Your request does not appear "
                "to match SHL assessment or "
                "hiring-related use cases."
            ),
            "recommendations": [],
            "end_of_conversation": False
        }


    # Build recommendation objects
    recommendations = []


    for result in results:

        item = result["item"]

        recommendations.append({

            "name": item.get("name", ""),

            "url": item.get("link", ""),

            "test_type": ", ".join(
                item.get("keys", [])
            ),

            "duration": item.get("duration", ""),

            "remote_testing": item.get("remote", ""),

            "adaptive_support": item.get("adaptive", ""),

            "description": (
                item.get("description", "")[:200]
            )
        })


    return {
        "reply": generate_reply(
            conversation_text,
            recommendations
        ),

        "recommendations": recommendations,

        "end_of_conversation": False
    }