from app.agents.tools import search_documents


def route_question(question):
    """Route a user question to the appropriate tool."""

    question_lower = question.lower()

    document_keywords = [
        "paper",
        "document",
        "research",
        "customer",
        "churn",
        "prediction",
        "model",
        "ann",
        "neural network",
        "machine learning"
    ]

    if any(
        keyword in question_lower
        for keyword in document_keywords
    ):
        return "document_search"

    return "unknown"


def execute_route(question):
    """Execute the tool selected by the router."""

    route = route_question(question)

    if route == "document_search":
        results = search_documents(question)

        return {
            "route": route,
            "results": results
        }

    return {
        "route": "unknown",
        "results": []
    }


if __name__ == "__main__":

    question = "What is customer churn prediction?"

    result = execute_route(question)

    print("\n========== AGENT ROUTER ==========")

    print(f"\nQuestion: {question}")
    print(f"Selected route: {result['route']}")

    print("\nTool Results:")

    for index, item in enumerate(
        result["results"],
        start=1
    ):
        print(f"\n--- Result {index} ---")
        print(f"Page: {item['page']}")
        print(f"Content: {item['content'][:300]}")