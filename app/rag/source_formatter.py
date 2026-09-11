def format_sources(documents):
    """Convert retrieved documents into clean source information."""

    sources = []

    for index, document in enumerate(documents, start=1):
        page = document.metadata.get(
            "page_label",
            document.metadata.get("page", "?")
        )

        source = document.metadata.get(
            "source",
            "Unknown source"
        )

        sources.append({
            "id": index,
            "source": source,
            "page": page
        })

    return sources


if __name__ == "__main__":
    from app.rag.retriever import retrieve_documents

    question = "What is customer churn prediction?"

    documents = retrieve_documents(
        question,
        k=10,
        top_k=3
    )

    sources = format_sources(documents)

    print("\nFormatted Sources:")

    for source in sources:
        print(
            f"[{source['id']}] "
            f"{source['source']} - "
            f"Page {source['page']}"
        )