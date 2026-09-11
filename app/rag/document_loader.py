from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader


# Path to our PDF document
PDF_PATH = Path("data/Customer Churn Prediction Research paper.pdf")


def load_pdf(pdf_path: Path):
    """Load a PDF and return its pages as LangChain documents."""

    loader = PyPDFLoader(str(pdf_path))

    documents = loader.load()

    return documents


if __name__ == "__main__":
    documents = load_pdf(PDF_PATH)

    print(f"Total pages loaded: {len(documents)}")

    print("\nFirst page preview:")
    print(documents[0].page_content[:1000])

    print("\nFirst page metadata:")
    print(documents[0].metadata)