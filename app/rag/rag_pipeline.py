from google import genai

from app.core.config import GEMINI_API_KEY
from app.rag.retriever import retrieve_documents
from app.rag.source_formatter import format_sources
from app.rag.memory import ConversationMemory


client = genai.Client(api_key=GEMINI_API_KEY)

memory = ConversationMemory()


def generate_rag_answer(question):
    """Retrieve, rerank, use conversation history and generate answer."""

    # Retrieve and rerank documents
    documents = retrieve_documents(
        question,
        k=10,
        top_k=3
    )

    # Combine retrieved chunks into context
    context = "\n\n".join(
        document.page_content
        for document in documents
    )

    # Get previous conversation
    history = memory.get_history()

    history_text = "\n".join(
        f"{message['role']}: {message['content']}"
        for message in history
    )

    # Create grounded prompt
    prompt = f"""
You are a helpful AI assistant answering questions based only on
the provided document context and conversation history.

Conversation history:
{history_text}

Document context:
{context}

Current question:
{question}

Instructions:
- Answer using only the provided document context.
- Use conversation history only to understand references or follow-up questions.
- If the answer is not available in the context, say:
  "I could not find this information in the provided document."
- Do not invent information.
"""

    # Generate answer using Gemini
    response = client.interactions.create(
        model="gemini-3.8-flash",
        input=prompt
    )

    answer = response.output_text

    # Save conversation
    memory.add_message("user", question)
    memory.add_message("assistant", answer)

    # Format sources
    sources = format_sources(documents)

    return answer, sources


if __name__ == "__main__":

    # ========================================
    # QUESTION 1
    # ========================================

    question_1 = "What is customer churn prediction?"

    answer_1, sources_1 = generate_rag_answer(question_1)

    print("\n========== QUESTION 1 ==========")
    print(question_1)

    print("\nANSWER 1:")
    print(answer_1)

    print("\nSOURCES FOR QUESTION 1:")

    for source in sources_1:
        print(
            f"[{source['id']}] "
            f"{source['source']} - "
            f"Page {source['page']}"
        )

    # ========================================
    # QUESTION 2 - FOLLOW-UP
    # ========================================

    question_2 = "Why is it important?"

    answer_2, sources_2 = generate_rag_answer(question_2)

    print("\n========== QUESTION 2 ==========")
    print(question_2)

    print("\nANSWER 2:")
    print(answer_2)

    print("\nSOURCES FOR QUESTION 2:")

    for source in sources_2:
        print(
            f"[{source['id']}] "
            f"{source['source']} - "
            f"Page {source['page']}"
        )

    # ========================================
    # CONVERSATION MEMORY
    # ========================================

    print("\n========== CONVERSATION MEMORY ==========")

    for message in memory.get_history():
        print(
            f"{message['role']}: {message['content']}"
        )