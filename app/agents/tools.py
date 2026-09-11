from app.rag.retriever import retrieve_documents


def search_documents(question, top_k=3):
    """Search the knowledge base and return relevant documents."""

    documents = retrieve_documents(
        question,
        k=10,
        top_k=top_k
    )

    results = []

    for document in documents:
        results.append({
            "content": document.page_content,
            "page": document.metadata.get(
                "page_label",
                document.metadata.get("page", "?")
            ),
            "source": document.metadata.get(
                "source",
                "Unknown source"
            )
        })

    return results


def get_document_sources(question):
    """Return only source information for a question."""

    documents = retrieve_documents(
        question,
        k=10,
        top_k=3
    )

    sources = []

    for document in documents:
        sources.append({
            "page": document.metadata.get(
                "page_label",
                document.metadata.get("page", "?")
            ),
            "source": document.metadata.get(
                "source",
                "Unknown source"
            )
        })

    return sources


if __name__ == "__main__":

    question = "What is customer churn prediction?"

    results = search_documents(question)

    print("\n========== DOCUMENT SEARCH TOOL ==========")

    for index, result in enumerate(results, start=1):

        print(f"\n--- Result {index} ---")
        print(f"Page: {result['page']}")
        print(f"Source: {result['source']}")
        print(f"Content: {result['content'][:500]}")