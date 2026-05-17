import json
import numpy as np
import faiss

from sentence_transformers import SentenceTransformer


# Load embedding model once
model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)


def load_catalog():

    with open(
        "../data/shl_catalog.json",
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def build_search_text(item):

    return f"""
    Name: {item.get('name', '')}

    Description:
    {item.get('description', '')}

    Categories:
    {' '.join(item.get('keys', []))}

    Job Levels:
    {' '.join(item.get('job_levels', []))}

    Languages:
    {' '.join(item.get('languages', []))}

    Remote Testing:
    {item.get('remote', '')}

    Adaptive Support:
    {item.get('adaptive', '')}

    Duration:
    {item.get('duration', '')}
    """


def create_embeddings(catalog):

    texts = []

    for item in catalog:

        search_text = build_search_text(item)

        texts.append(search_text)

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        show_progress_bar=True
    )

    embeddings = embeddings.astype("float32")

    return embeddings


def build_faiss_index(embeddings):

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)

    index.add(embeddings)

    return index


def search_assessments(
    query,
    catalog,
    index,
    top_k=10
):

    query_embedding = model.encode(
        [query],
        convert_to_numpy=True
    )

    query_embedding = query_embedding.astype(
        "float32"
    )

    distances, indices = index.search(
        query_embedding,
        top_k
    )

    results = []

    technical_keywords = [
        "java",
        "python",
        "developer",
        "backend",
        "frontend",
        "software",
        "coding",
        "programming",
        "sql",
        "api",
        "microservices",
        "spring",
        "react",
        "node"
    ]

    is_technical_query = any(
        word in query.lower()
        for word in technical_keywords
    )

    for idx, distance in zip(
        indices[0],
        distances[0]
    ):

        if idx == -1:
            continue

        item = catalog[idx]

        score = float(distance)

        # Technical relevance boosting
        if is_technical_query:

            description = item.get(
                "description",
                ""
            ).lower()

            keys = " ".join(
                item.get("keys", [])
            ).lower()

            name = item.get(
                "name",
                ""
            ).lower()

            technical_terms = [
                "java",
                "python",
                "coding",
                "software",
                "developer",
                "programming",
                "sql",
                "api",
                "technical"
            ]

            if any(
                term in description
                for term in technical_terms
            ):
                score -= 0.25

            if any(
                term in name
                for term in technical_terms
            ):
                score -= 0.25

            if (
                "knowledge & skills"
                in keys
            ):
                score -= 0.30

        is_relevant = True

    if is_technical_query:

        relevant_terms = [
            "java",
            "software",
            "developer",
            "coding",
            "programming",
            "technical",
            "api",
            "sql",
            "backend",
            "web services"
        ]

        searchable_text = (
            item.get("name", "") + " " +
            item.get("description", "") + " " +
            " ".join(item.get("keys", []))
        ).lower()

        match_count = sum(
            1
            for term in relevant_terms
            if term in searchable_text
        )

        # Reject only extremely unrelated results
        if match_count == 0 and score > 1.0:
            is_relevant = False


    if is_relevant:

        results.append({
            "item": item,
            "distance": score
        })

    # Sort after boosting
    results = sorted(
        results,
        key=lambda x: x["distance"]
    )

    return results