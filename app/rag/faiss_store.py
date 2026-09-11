from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from app.rag.document_loader import load_pdf
from app.rag.text_splitter import split_documents


VECTOR_STORE_PATH = Path("data/vector_store")

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


def create_vector_store(chunks):
    """Create a new FAISS vector store from document chunks."""

    if not chunks:
        raise ValueError(
            "No document chunks were provided."
        )

    vector_store = FAISS.from_documents(
        chunks,
        embedding_model
    )

    return vector_store


def load_vector_store():
    """Load the existing FAISS vector store from disk."""

    vector_store = FAISS.load_local(
        str(VECTOR_STORE_PATH),
        embedding_model,
        allow_dangerous_deserialization=True
    )

    return vector_store


def save_vector_store(vector_store):
    """Save the FAISS vector store to disk."""

    VECTOR_STORE_PATH.mkdir(
        parents=True,
        exist_ok=True
    )

    vector_store.save_local(
        str(VECTOR_STORE_PATH)
    )


def add_pdf_to_vector_store(pdf_path):
    """
    Process a new PDF and add its chunks
    to the existing FAISS vector store.
    """

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF not found: {pdf_path}"
        )

    documents = load_pdf(pdf_path)

    chunks = split_documents(documents)

    if not chunks:
        raise ValueError(
            "No text chunks were created from the PDF."
        )

    vector_store = load_vector_store()

    vector_store.add_documents(
        chunks
    )

    save_vector_store(
        vector_store
    )

    return {
        "documents": len(documents),
        "chunks": len(chunks),
        "pdf_path": str(pdf_path),
    }


def rebuild_vector_store(pdf_paths):
    """
    Completely rebuild the FAISS vector store
    from the provided PDF files.
    """

    pdf_paths = [
        Path(pdf_path)
        for pdf_path in pdf_paths
    ]

    all_chunks = []
    document_stats = []

    for pdf_path in pdf_paths:

        if not pdf_path.exists():
            raise FileNotFoundError(
                f"PDF not found: {pdf_path}"
            )

        documents = load_pdf(
            pdf_path
        )

        chunks = split_documents(
            documents
        )

        if not chunks:
            raise ValueError(
                f"No text chunks were created from: {pdf_path.name}"
            )

        all_chunks.extend(
            chunks
        )

        document_stats.append({
            "filename": pdf_path.name,
            "pages": len(documents),
            "chunks": len(chunks),
        })

    vector_store = create_vector_store(
        all_chunks
    )

    save_vector_store(
        vector_store
    )

    return {
        "documents": len(pdf_paths),
        "pages": sum(
            item["pages"]
            for item in document_stats
        ),
        "chunks": len(all_chunks),
        "stats": document_stats,
    }


if __name__ == "__main__":

    PDF_PATHS = [
        Path(
            "data/Customer Churn Prediction Research paper.pdf"
        ),
        Path(
            "data/Minor Project Report DBMS (1).pdf"
        ),
    ]

    result = rebuild_vector_store(
        PDF_PATHS
    )

    print(
        "\nFAISS vector store rebuilt successfully."
    )

    print(
        f"Total documents: {result['documents']}"
    )

    print(
        f"Total pages: {result['pages']}"
    )

    print(
        f"Total chunks: {result['chunks']}"
    )

    print(
        f"Vector store path: {VECTOR_STORE_PATH}"
    )

    print("\nDocument details:")

    for item in result["stats"]:
        print(
            f"- {item['filename']}: "
            f"{item['pages']} pages, "
            f"{item['chunks']} chunks"
        )