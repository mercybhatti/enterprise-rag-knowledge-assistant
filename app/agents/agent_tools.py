from app.agents.tools import search_documents


AVAILABLE_TOOLS = {
    "document_search": {
        "name": "document_search",
        "description": (
            "Search the uploaded research document for relevant "
            "information."
        ),
        "function": search_documents
    }
}


def get_available_tools():
    """Return the tools available to the agent."""

    return AVAILABLE_TOOLS


def execute_tool(tool_name, question):
    """Execute a selected agent tool."""

    if tool_name not in AVAILABLE_TOOLS:
        raise ValueError(
            f"Unknown tool: {tool_name}"
        )

    tool = AVAILABLE_TOOLS[tool_name]

    return tool["function"](question)


if __name__ == "__main__":

    print("\n========== AVAILABLE AGENT TOOLS ==========")

    tools = get_available_tools()

    for tool_name, tool in tools.items():

        print(f"\nTool: {tool_name}")
        print(f"Description: {tool['description']}")

    question = "What is customer churn prediction?"

    print("\n========== TOOL EXECUTION ==========")

    results = execute_tool(
        "document_search",
        question
    )

    print(f"\nRetrieved results: {len(results)}")

    for index, result in enumerate(
        results,
        start=1
    ):
        print(
            f"\nResult {index} - Page {result['page']}"
        )