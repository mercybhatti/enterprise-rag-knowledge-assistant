from pathlib import Path

from sentence_transformers import SentenceTransformer

from app.rag.document_loader import load_pdf
from app.rag.text_splitter import split_documents


PDF_PATH = Path("data/Customer Churn Prediction Research paper.pdf")

# Load the embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def create_embeddings(documents):
    """Convert document chunks into numerical vectors."""

    texts = [document.page_content for document in documents]

    embeddings = embedding_model.encode(
        texts,
        show_progress_bar=True
    )

    return embeddings


if __name__ == "__main__":
    # Load PDF
    documents = load_pdf(PDF_PATH)

    # Split PDF into chunks
    chunks = split_documents(documents)

    # Create embeddings
    embeddings = create_embeddings(chunks)

    print(f"\nTotal chunks: {len(chunks)}")
    print(f"Embedding shape: {embeddings.shape}")

    print("\nFirst embedding:")
    print(embeddings[0])