from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel, Field

from app.agents.tools import search_documents
from app.agents.gemini_agent import run_agent
from app.services.document_service import upload_and_index_document


app = FastAPI(
    title="Enterprise RAG Knowledge Assistant",
    description="AI-powered document question answering system.",
    version="1.0.0"
)


# ============================================================
# REQUEST / RESPONSE MODELS
# ============================================================

class ChatRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        description="Question to ask about the knowledge base."
    )


class SearchResponse(BaseModel):
    question: str
    results: list
    sources: list


class ChatResponse(BaseModel):
    question: str
    answer: str
    sources: list


class DocumentUploadResponse(BaseModel):
    message: str
    document_id: int
    filename: str
    pages: int
    chunks: int


# ============================================================
# SOURCE FORMATTER
# ============================================================

def build_sources(results):
    """Build clean source information from search results."""

    sources = []

    for index, result in enumerate(results, start=1):
        sources.append({
            "id": index,
            "source": result["source"],
            "page": result["page"]
        })

    return sources


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    """Return basic API information."""

    return {
        "message": "Enterprise RAG Knowledge Assistant API is running.",
        "version": "1.0.0"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():
    """Check whether the API is healthy."""

    return {
        "status": "healthy"
    }


# ============================================================
# DOCUMENT SEARCH
# ============================================================

@app.post(
    "/search",
    response_model=SearchResponse
)
def search(request: ChatRequest):
    """
    Search the knowledge base using
    semantic retrieval and reranking.
    """

    try:
        results = search_documents(
            request.question,
            top_k=3
        )

        sources = build_sources(results)

        return SearchResponse(
            question=request.question,
            results=results,
            sources=sources
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Document search failed: {error}"
        )


# ============================================================
# AI CHAT
# ============================================================

@app.post(
    "/chat",
    response_model=ChatResponse
)
def chat(request: ChatRequest):
    """
    Answer a user question using the Gemini agent.

    Flow:

    User question
        ↓
    Gemini Agent
        ↓
    document_search tool
        ↓
    FAISS retrieval
        ↓
    Cross-encoder reranking
        ↓
    Relevant document context
        ↓
    Gemini grounded answer
    """

    try:
        # ----------------------------------------------------
        # 1. Retrieve sources for the response
        # ----------------------------------------------------

        results = search_documents(
            request.question,
            top_k=3
        )

        sources = build_sources(results)

        # ----------------------------------------------------
        # 2. Handle no relevant documents
        # ----------------------------------------------------

        if not results:
            return ChatResponse(
                question=request.question,
                answer=(
                    "I could not find relevant information "
                    "in the provided knowledge base."
                ),
                sources=[]
            )

        # ----------------------------------------------------
        # 3. Run the Gemini agent
        # ----------------------------------------------------

        answer = run_agent(
            request.question
        )

        # ----------------------------------------------------
        # 4. Return grounded answer + sources
        # ----------------------------------------------------

        return ChatResponse(
            question=request.question,
            answer=answer,
            sources=sources
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Chat request failed: {error}"
        )


# ============================================================
# DOCUMENT UPLOAD
# ============================================================

@app.post(
    "/documents/upload",
    response_model=DocumentUploadResponse
)
def upload_document(
    file: UploadFile = File(...)
):
    """
    Upload a PDF, index it in FAISS,
    and register it in the database.
    """

    try:
        # ----------------------------------------------------
        # 1. Validate filename
        # ----------------------------------------------------

        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="No filename was provided."
            )

        # ----------------------------------------------------
        # 2. Validate file type
        # ----------------------------------------------------

        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are supported."
            )

        # ----------------------------------------------------
        # 3. Save + index + register document
        # ----------------------------------------------------

        result = upload_and_index_document(
            file.file,
            file.filename
        )

        # ----------------------------------------------------
        # 4. Return upload result
        # ----------------------------------------------------

        return DocumentUploadResponse(
            message="Document uploaded and indexed successfully.",
            document_id=result["document_id"],
            filename=result["filename"],
            pages=result["pages"],
            chunks=result["chunks"]
        )

    except HTTPException:
        raise

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Document upload failed: {error}"
        )

    finally:
        file.file.close()