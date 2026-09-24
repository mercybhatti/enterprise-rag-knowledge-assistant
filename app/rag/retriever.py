from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from app.rag.reranker import rerank_documents


VECTOR_STORE_PATH = "data/vector_store"

# Load embedding model only when required.
embedding_model = None


def get_embedding_model():
    """Load and return the embedding model when needed."""

    global embedding_model

    if embedding_model is None:
        embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

    return embedding_model


def load_vector_store():
    """Load the saved FAISS vector store."""

    vector_store = FAISS.load_local(
        VECTOR_STORE_PATH,
        get_embedding_model(),
        allow_dangerous_deserialization=True
    )

    return vector_store


def retrieve_documents(question, k=10, top_k=3):
    """Retrieve candidates from FAISS and rerank the best results."""

    vector_store = load_vector_store()

    # Step 1: Retrieve initial candidates
    documents = vector_store.similarity_search(
        question,
        k=k
    )

    # Step 2: Rerank candidates
    reranked_documents = rerank_documents(
        question,
        documents,
        top_k=top_k
    )

    return reranked_documents


if __name__ == "__main__":

    question = "What is customer churn prediction?"

    documents = retrieve_documents(
        question,
        k=10,
        top_k=3
    )

    print(f"Question: {question}")
    print(f"\nFinal retrieved documents: {len(documents)}")

    for i, document in enumerate(documents, start=1):

        print(f"\n--- Result {i} ---")

        print(document.page_content[:700])

        print("\nMetadata:")
        print(document.metadata)