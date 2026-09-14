from io import BytesIO

from fastapi.testclient import TestClient

from app.api.main import app


client = TestClient(app)


# ============================================================
# INVALID FILE TYPE TEST
# ============================================================

def test_upload_rejects_non_pdf_file():
    """
    Test that the upload endpoint rejects files
    that are not PDF files.
    """

    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "test.txt",
                BytesIO(b"This is not a PDF file."),
                "text/plain"
            )
        }
    )

    assert response.status_code == 400

    data = response.json()

    assert data["detail"] == "Only PDF files are supported."


# ============================================================
# DUPLICATE DOCUMENT TEST
# ============================================================

def test_upload_rejects_duplicate_document():
    """
    Test that an already registered document
    cannot be uploaded again.
    """

    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "Customer Churn Prediction Research paper.pdf",
                BytesIO(b"Fake PDF content for duplicate test."),
                "application/pdf"
            )
        }
    )

    assert response.status_code == 400

    data = response.json()

    assert data["detail"] == "This document is already registered."