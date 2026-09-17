# Enterprise RAG Knowledge Assistant

An end-to-end Retrieval-Augmented Generation (RAG) based AI knowledge assistant that allows users to upload PDF documents, search their knowledge base, and ask questions using grounded AI responses with source references.

The project combines document processing, embeddings, FAISS vector search, semantic retrieval, cross-encoder reranking, Gemini-powered agentic question answering, FastAPI, Streamlit, authentication, conversation persistence, and Docker.

---

## Features

- PDF document upload and indexing
- Automatic document text extraction
- Text chunking for retrieval
- Semantic embeddings
- FAISS vector database
- Semantic document retrieval
- Cross-encoder reranking
- Gemini-powered grounded responses
- Agentic document search workflow
- Source and page references
- FastAPI backend
- Streamlit frontend
- User registration and login
- Persistent authentication sessions
- Conversation history
- Create new conversations
- Reopen previous conversations
- Delete conversations
- Persistent knowledge base across conversations
- Duplicate document detection
- Docker containerization

---

## System Architecture

```text
                    ┌──────────────────────┐
                    │     Streamlit UI     │
                    │   Authentication     │
                    │  Chat + Conversations│
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │     FastAPI API       │
                    │                      │
                    │ /chat               │
                    │ /search             │
                    │ /documents/upload   │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    Gemini Agent      │
                    │                      │
                    │   document_search    │
                    │        tool          │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Retrieval Layer    │
                    │                      │
                    │ Embeddings → FAISS   │
                    │ Retrieval → Reranking│
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    Knowledge Base    │
                    │                      │
                    │       PDF Docs       │
                    └──────────────────────┘