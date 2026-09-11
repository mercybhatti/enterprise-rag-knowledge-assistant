from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.rag.document_loader import load_pdf


PDF_PATH = Path("data/Customer Churn Prediction Research paper.pdf")


def split_documents(documents):
    """Split loaded documents into smaller chunks."""

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )

    chunks = text_splitter.split_documents(documents)

    return chunks


if __name__ == "__main__":
    documents = load_pdf(PDF_PATH)

    chunks = split_documents(documents)

    print(f"Total pages: {len(documents)}")
    print(f"Total chunks: {len(chunks)}")

    print("\nFirst chunk:")
    print(chunks[0].page_content)

    print("\nFirst chunk metadata:")
    print(chunks[0].metadata)