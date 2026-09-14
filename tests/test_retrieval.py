from app.agents.tools import search_documents


# ============================================================
# RETRIEVAL TEST
# ============================================================

def test_customer_churn_retrieval():
    """
    Test that the knowledge base can retrieve
    relevant documents for a customer churn question.
    """

    question = "What is customer churn prediction?"

    results = search_documents(
        question,
        top_k=3
    )

    # We should receive results from the knowledge base.
    assert len(results) > 0

    # The requested number of results should not be exceeded.
    assert len(results) <= 3

    # Every result should contain the fields
    # required by our application.
    for result in results:
        assert "content" in result
        assert "page" in result
        assert "source" in result

        assert result["content"]
        assert result["page"]
        assert result["source"]

    # The customer churn research paper should be
    # among the retrieved sources.
    assert any(
        "Customer Churn Prediction Research paper.pdf"
        in result["source"]
        for result in results
    )