import json
import os

from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def analyze_conversation(conversation_text):

    prompt = f"""
You are an SHL hiring assistant.

Your task:
1. Decide whether enough hiring information exists
2. If not, ask ONE follow-up question
3. If enough information exists, return READY

Conversation:
{conversation_text}

Return ONLY valid JSON.

Example:
{{
    "status": "follow_up",
    "question": "What is the seniority level required?"
}}

OR

{{
    "status": "ready"
}}
"""

    try:

        response = client.chat.completions.create(

            model="llama-3.3-70b-versatile",

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0
        )

        text = response.choices[0].message.content

        data = json.loads(text)

        return data

    except Exception as e:

        print(e)

        return {
            "status": "ready"
        }


def generate_reply(query, recommendations):

    prompt = f"""
You are an SHL hiring assistant.

User request:
{query}

Recommendations:
{recommendations}

Write a concise professional response.
"""

    try:

        response = client.chat.completions.create(

            model="llama-3.3-70b-versatile",

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0.3
        )

        return response.choices[0].message.content

    except Exception:

        return (
            "Here are recommended SHL assessments "
            "based on your hiring requirements."
        )