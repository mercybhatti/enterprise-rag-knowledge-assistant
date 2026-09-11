import json

from google import genai

from app.core.config import GEMINI_API_KEY
from app.agents.tools import search_documents


# ============================================================
# GEMINI CLIENT
# ============================================================

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# ============================================================
# DOCUMENT SEARCH TOOL DEFINITION
# ============================================================

DOCUMENT_SEARCH_TOOL = {
    "type": "function",
    "name": "document_search",
    "description": (
        "Search the uploaded knowledge base for information "
        "relevant to the user's question."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": (
                    "The user's question to search in the knowledge base."
                )
            }
        },
        "required": ["question"]
    }
}


# ============================================================
# DOCUMENT SEARCH
# ============================================================

def run_document_search(question):
    """Execute the document search tool."""

    return search_documents(
        question,
        top_k=3
    )


# ============================================================
# AGENT INSTRUCTIONS
# ============================================================

def get_agent_instructions():
    """Return the instructions used by the Gemini agent."""

    return """
You are an intelligent knowledge assistant.

Your job is to answer questions using the uploaded
knowledge base.

When the user asks something related to the knowledge base,
use the document_search tool.

Do not invent information.

Use only information returned by the document_search tool.

If the required information cannot be found in the
knowledge base, clearly say that the information
was not found.

Always provide a clear text answer after using the
document_search tool.
"""


# ============================================================
# TOOL CONTEXT BUILDER
# ============================================================

def build_tool_context(results):
    """Convert search results into readable context."""

    context_parts = []

    for index, result in enumerate(results, start=1):
        context_parts.append(
            f"""
Source {index}
Page: {result['page']}
Document: {result['source']}

Content:
{result['content']}
"""
        )

    return "\n".join(context_parts)


# ============================================================
# OUTPUT VALIDATION
# ============================================================

def validate_agent_output(output_text):
    """
    Validate Gemini's final text response.

    Returns a clean answer when valid.
    Raises ValueError when Gemini returns an empty response.
    """

    if output_text is None:
        raise ValueError(
            "Gemini returned no response."
        )

    answer = output_text.strip()

    if not answer:
        raise ValueError(
            "Gemini returned an empty response."
        )

    return answer


# ============================================================
# FALLBACK ANSWER GENERATION
# ============================================================

def generate_fallback_answer(question, results):
    """
    Generate a grounded answer using the retrieved
    document context when the agent interaction
    returns an empty response.
    """

    if not results:
        return (
            "I could not find relevant information "
            "in the provided knowledge base."
        )

    context = build_tool_context(
        results
    )

    fallback_prompt = f"""
You are a knowledge assistant.

Answer the user's question using ONLY the
retrieved information provided below.

Do not invent facts.

If the retrieved information does not contain
the answer, clearly say that the information
was not found in the provided knowledge base.

Retrieved document context:

{context}

User question:

{question}

Provide a clear and concise answer.
"""

    fallback_interaction = client.interactions.create(
        model="gemini-3.8-flash",
        input=fallback_prompt
    )

    return validate_agent_output(
        fallback_interaction.output_text
    )


# ============================================================
# GEMINI AGENT
# ============================================================

def run_agent(question):
    """
    Run the Gemini agent with document search
    tool calling and a grounded fallback.
    """

    # --------------------------------------------------------
    # 1. Send the question to Gemini
    # --------------------------------------------------------

    interaction = client.interactions.create(
        model="gemini-3.8-flash",
        input=(
            f"{get_agent_instructions()}\n\n"
            f"User question:\n{question}"
        ),
        tools=[DOCUMENT_SEARCH_TOOL]
    )

    final_interaction = interaction
    retrieved_results = []

    # --------------------------------------------------------
    # 2. Check whether Gemini requested a tool call
    # --------------------------------------------------------

    for step in interaction.steps:

        if step.type != "function_call":
            continue

        if step.name != "document_search":
            continue

        # ----------------------------------------------------
        # 3. Get the question requested by the agent
        # ----------------------------------------------------

        tool_question = step.arguments.get(
            "question",
            question
        )

        # ----------------------------------------------------
        # 4. Execute our local document search
        # ----------------------------------------------------

        retrieved_results = run_document_search(
            tool_question
        )

        # ----------------------------------------------------
        # 5. Send tool results back to Gemini
        # ----------------------------------------------------

        tool_result = [
            {
                "type": "text",
                "text": json.dumps(
                    retrieved_results,
                    ensure_ascii=False
                )
            }
        ]

        final_interaction = client.interactions.create(
            model="gemini-3.8-flash",
            previous_interaction_id=interaction.id,
            input=[
                {
                    "type": "function_result",
                    "name": step.name,
                    "call_id": step.id,
                    "result": tool_result
                }
            ],
            tools=[DOCUMENT_SEARCH_TOOL]
        )

    # --------------------------------------------------------
    # 6. Try to use the agent's final response
    # --------------------------------------------------------

    try:
        answer = validate_agent_output(
            final_interaction.output_text
        )

        return answer

    except ValueError:

        # ----------------------------------------------------
        # 7. Fallback if Gemini returned an empty response
        # ----------------------------------------------------

        if not retrieved_results:
            retrieved_results = run_document_search(
                question
            )

        return generate_fallback_answer(
            question,
            retrieved_results
        )