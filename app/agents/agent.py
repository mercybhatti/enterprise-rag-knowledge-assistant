from app.agents.agent_tools import execute_tool


class KnowledgeAgent:
    """Agent that decides which tool to use for a question."""

    def decide_tool(self, question):
        """Decide which tool should handle the question."""

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

        return None

    def run(self, question):
        """Run the agent and execute the selected tool."""

        tool_name = self.decide_tool(question)

        if tool_name is None:
            return {
                "tool": None,
                "results": []
            }

        results = execute_tool(
            tool_name,
            question
        )

        return {
            "tool": tool_name,
            "results": results
        }


if __name__ == "__main__":

    agent = KnowledgeAgent()

    question = "What is customer churn prediction?"

    result = agent.run(question)

    print("\n========== KNOWLEDGE AGENT ==========")

    print(f"\nQuestion:")
    print(question)

    print(f"\nSelected Tool:")
    print(result["tool"])

    print(f"\nRetrieved Results:")
    print(len(result["results"]))

    for index, item in enumerate(
        result["results"],
        start=1
    ):
        print(
            f"\n--- Result {index} ---"
        )

        print(
            f"Page: {item['page']}"
        )

        print(
            f"Content: {item['content'][:300]}"
        )