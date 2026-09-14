from pathlib import Path
import shutil

from app.database.database import (
    create_document,
    get_document_by_filename,
)
from app.rag.faiss_store import add_pdf_to_vector_store


# ============================================================
# DOCUMENT CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"

ALLOWED_EXTENSIONS = {".pdf"}


# ============================================================
# DOCUMENT VALIDATION
# ============================================================

def validate_pdf(filename):
    """Validate that the uploaded file is a PDF."""

    if not filename:
        return False, "Filename is required."

    file_path = Path(filename)

    if file_path.suffix.lower() not in ALLOWED_EXTENSIONS:
        return False, "Only PDF files are supported."

    return True, ""


# ============================================================
# DOCUMENT UPLOAD
# ============================================================

def save_uploaded_pdf(uploaded_file, filename):
    """
    Save an uploaded PDF into the project's data directory.

    Duplicate checking is performed before this function
    writes the file to disk.
    """

    if uploaded_file is None:
        raise ValueError(
            "No file was provided."
        )

    if not filename:
        raise ValueError(
            "Filename is required."
        )

    filename = Path(filename).name

    is_valid, message = validate_pdf(
        filename
    )

    if not is_valid:
        raise ValueError(
            message
        )

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    destination = DATA_DIR / filename

    with destination.open("wb") as file:
        shutil.copyfileobj(
            uploaded_file,
            file
        )

    return destination


# ============================================================
# DOCUMENT INDEXING
# ============================================================

def index_document(pdf_path):
    """
    Add a PDF to FAISS and register it in SQLite.
    """

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF not found: {pdf_path}"
        )

    # --------------------------------------------------------
    # Prevent duplicate document registration
    # --------------------------------------------------------

    existing_document = get_document_by_filename(
        pdf_path.name
    )

    if existing_document is not None:
        raise ValueError(
            "This document is already registered."
        )

    # --------------------------------------------------------
    # Add PDF to FAISS
    # --------------------------------------------------------

    result = add_pdf_to_vector_store(
        pdf_path
    )

    # --------------------------------------------------------
    # Register document in SQLite
    # --------------------------------------------------------

    document_id = create_document(
        filename=pdf_path.name,
        file_path=str(pdf_path),
        page_count=result["documents"],
        chunk_count=result["chunks"],
    )

    if document_id is None:
        raise RuntimeError(
            "Document was indexed but could not be registered "
            "in the database."
        )

    return {
        "document_id": document_id,
        "filename": pdf_path.name,
        "pages": result["documents"],
        "chunks": result["chunks"],
        "file_path": str(pdf_path),
    }


# ============================================================
# COMPLETE UPLOAD + INDEX WORKFLOW
# ============================================================

def upload_and_index_document(uploaded_file, filename):
    """
    Save an uploaded PDF, index it in FAISS,
    and register it in SQLite.

    Duplicate checking happens before the file is saved.
    """

    if uploaded_file is None:
        raise ValueError(
            "No file was provided."
        )

    if not filename:
        raise ValueError(
            "Filename is required."
        )

    filename = Path(filename).name

    is_valid, message = validate_pdf(
        filename
    )

    if not is_valid:
        raise ValueError(
            message
        )

    # --------------------------------------------------------
    # Check duplicate BEFORE writing to disk
    # --------------------------------------------------------

    existing_document = get_document_by_filename(
        filename
    )

    if existing_document is not None:
        raise ValueError(
            "This document is already registered."
        )

    # --------------------------------------------------------
    # Save the PDF
    # --------------------------------------------------------

    pdf_path = save_uploaded_pdf(
        uploaded_file,
        filename
    )

    # --------------------------------------------------------
    # Index and register the document
    # --------------------------------------------------------

    result = index_document(
        pdf_path
    )

    return result