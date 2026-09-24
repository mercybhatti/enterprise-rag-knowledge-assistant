from sentence_transformers import CrossEncoder


# Load the reranker model only when it is actually required.
# This avoids loading the model during application startup.
reranker_model = None


def get_reranker_model():
    """Load and return the reranker model when needed."""

    global reranker_model

    if reranker_model is None:
        reranker_model = CrossEncoder(
            "cross-encoder/ms-marco-MiniLM-L-6-v2"
        )

    return reranker_model


def rerank_documents(question, documents, top_k=3):
    """Rerank retrieved documents using a cross-encoder."""

    if not documents:
        return []

    pairs = [
        [question, document.page_content]
        for document in documents
    ]

    model = get_reranker_model()

    scores = model.predict(pairs)

    ranked_documents = sorted(
        zip(documents, scores),
        key=lambda x: x[1],
        reverse=True
    )

    return [
        document
        for document, score in ranked_documents[:top_k]
    ]