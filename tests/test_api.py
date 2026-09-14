from fastapi.testclient import TestClient

from app.api.main import app
from app.agents.gemini_agent import GeminiQuotaError


client = TestClient(app)


# ============================================================
# ROOT ENDPOINT TEST
# ============================================================

def test_root():
    """Test that the root API endpoint is working."""

    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == (
        "Enterprise RAG Knowledge Assistant API is running."
    )

    assert data["version"] == "1.0.0"


# ============================================================
# HEALTH ENDPOINT TEST
# ============================================================

def test_health():
    """Test that the health check endpoint is working."""

    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"


# ============================================================
# CHAT REQUEST VALIDATION TEST
# ============================================================

def test_chat_rejects_empty_question():
    """Test that an empty question is rejected."""

    response = client.post(
        "/chat",
        json={
            "question": ""
        }
    )

    assert response.status_code == 422


# ============================================================
# SEARCH REQUEST VALIDATION TEST
# ============================================================

def test_search_rejects_empty_question():
    """Test that an empty search question is rejected."""

    response = client.post(
        "/search",
        json={
            "question": ""
        }
    )

    assert response.status_code == 422


# ============================================================
# GEMINI QUOTA ERROR TEST
# ============================================================

def test_chat_returns_429_when_gemini_quota_is_exceeded(
    monkeypatch
):
    """
    Test that a Gemini quota error is returned
    by the API as HTTP 429 instead of HTTP 500.
    """

    fake_results = [
        {
            "content": "Customer churn prediction content.",
            "page": "2",
            "source": (
                "data\\Customer Churn Prediction "
                "Research paper.pdf"
            )
        }
    ]

    def fake_search_documents(question, top_k=3):
        return fake_results

    def fake_run_agent(question):
        raise GeminiQuotaError(
            "The AI service is temporarily unavailable "
            "because the Gemini free-tier quota has been "
            "reached. Please try again later."
        )

    monkeypatch.setattr(
        "app.api.main.search_documents",
        fake_search_documents
    )

    monkeypatch.setattr(
        "app.api.main.run_agent",
        fake_run_agent
    )

    response = client.post(
        "/chat",
        json={
            "question": "What is customer churn prediction?"
        }
    )

    assert response.status_code == 429

    data = response.json()

    assert "Gemini free-tier quota" in data["detail"]