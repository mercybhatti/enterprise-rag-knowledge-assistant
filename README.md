# Enterprise RAG Knowledge Assistant

An end-to-end Retrieval-Augmented Generation (RAG) application that allows users to build a personal knowledge base from PDF documents and ask questions using AI-generated answers grounded in their uploaded content.

The system combines document processing, semantic search, vector retrieval, cross-encoder reranking, and a Gemini-powered agentic workflow to provide relevant answers with source and page references.

It also includes user authentication, persistent conversations, document management, a FastAPI backend, a Streamlit frontend, and Docker-based deployment support.

---

## Project Overview

The Enterprise RAG Knowledge Assistant is designed to make document-based information retrieval faster and more reliable.

Instead of manually searching through multiple PDF documents, users can upload their documents, build a searchable knowledge base, and ask questions in natural language.

The system retrieves relevant document content before generating a response, helping reduce unsupported answers and allowing users to verify the information through source references.

---

## Key Features

### Document Processing

- Upload PDF documents
- Extract text from documents
- Split text into smaller chunks
- Generate semantic embeddings
- Index documents for future retrieval
- Detect duplicate documents

### Retrieval and Question Answering

- Semantic similarity search
- FAISS-based vector search
- Cross-encoder reranking
- Gemini-powered answer generation
- Agentic document search workflow
- Grounded responses based on uploaded documents
- Source and page references

### User and Conversation Management

- User registration and login
- Persistent authentication sessions
- Create new conversations
- View previous conversations
- Reopen saved conversations
- Delete conversations
- Maintain a persistent knowledge base across conversations

### Application and Deployment

- FastAPI backend
- Streamlit frontend
- Docker containerization
- Separate API and user interface layers

---

## How It Works

The application follows the workflow below:

1. The user uploads one or more PDF documents.
2. The system extracts text from the uploaded documents.
3. The extracted text is divided into smaller chunks.
4. Embeddings are generated for the text chunks.
5. The embeddings are stored in a FAISS vector index.
6. When the user asks a question, relevant chunks are retrieved.
7. A cross-encoder reranker improves the relevance of retrieved results.
8. The Gemini-powered agent uses the retrieved content to generate an answer.
9. The response is displayed with source and page references where available.
10. Conversations are stored so users can revisit them later.

---

## System Architecture

```text
                    ┌──────────────────────────┐
                    │       Streamlit UI       │
                    │                          │
                    │ Authentication           │
                    │ PDF Upload               │
                    │ Chat Interface           │
                    │ Conversation Management  │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │        FastAPI API       │
                    │                          │
                    │ /chat                    │
                    │ /search                  │
                    │ /documents/upload        │
                    │ Authentication APIs      │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │      Gemini Agent        │
                    │                          │
                    │Agentic Question Answering│
                    │ document_search Tool     │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │      Retrieval Layer     │
                    │                          │
                    │ Text Embeddings          │
                    │ FAISS Vector Search      │
                    │ Semantic Retrieval       │
                    │ Cross-Encoder Reranking  │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │      Knowledge Base      │
                    │                          │
                    │ Uploaded PDF Documents   │
                    │ Indexed Text Chunks      │
                    └──────────────────────────┘

Technology Stack

Layer                  Technologies

Frontend               Streamlit
Backend                FastAPI
Programming Language   Python
Large Language Model   Google Gemini
Retrieval Method       Retrieval-Augmented Generation
Vector Database        FAISS
Embeddings             Semantic Text Embeddings
Reranking              Cross-Encoder
Document Input         PDF Documents
Authentication         Application-level user authentication
Containerization       Docker

Main Components
1. Document Ingestion
Responsible for accepting PDF files, extracting their text, splitting the content into chunks, and preparing the content for indexing.

2. Embedding Generation
Converts text chunks into numerical vector representations so that semantically similar content can be retrieved even when the exact keywords are different.

3. FAISS Vector Search
Stores and searches document embeddings efficiently to identify content relevant to the user's question.

4. Cross-Encoder Reranking
Reorders the retrieved results based on their relevance to the user's query, improving the quality of the final context provided to the language model.

5. Gemini Agent
Uses the retrieved document context and the document search tool to generate natural-language answers grounded in the available knowledge base.

6. FastAPI Backend
Provides API endpoints for authentication, document upload, search, chat, and application operations.

7. Streamlit Frontend
Provides the user interface for document uploads, chatting with the knowledge base, and managing conversations.

Example Use Cases

The application can be used for:
Searching through company documentation
Asking questions about technical PDFs
Exploring research papers
Querying internal knowledge documents
Finding specific information from large document collections
Creating a personal document-based AI assistant

Project Structure
enterprise-rag-knowledge-assistant/
│
├── backend/
│   ├── API and application logic
│   ├── Authentication
│   ├── Chat endpoints
│   ├── Search endpoints
│   └── Document upload handling
│
├── frontend/
│   └── Streamlit user interface
│
├── data/
│   └── Local document and knowledge-base data
│
├── requirements.txt
├── Dockerfile
├── .env
├── .gitignore
└── README.md

The exact project structure may vary depending on the current implementation and deployment configuration.

Running the Project
1. Clone the Repository
git clone https://github.com/mercybhatti/enterprise-rag-knowledge-assistant.git
2. Navigate to the Project Directory
cd enterprise-rag-knowledge-assistant
3. Create and Activate a Virtual Environment

On Windows:
py -3.12 -m venv venv

Activate the environment:
.\venv\Scripts\activate
4. Install Dependencies
pip install -r requirements.txt
5. Configure Environment Variables

Create a .env file in the project root and add the required configuration values.

Example:

GEMINI_API_KEY=your_api_key_here
Do not commit API keys or other sensitive credentials to GitHub.

6. Start the Application
Run the backend and frontend using the commands configured for the current project structure.

Docker Support
The project includes Docker support for running the application in a containerized environment.

Build the Docker image:
docker build -t enterprise-rag-assistant .

Run the container:
docker run -p 8000:8000 enterprise-rag-assistant

The backend can then be accessed through the configured FastAPI port.
Security and Data Handling
API keys are stored through environment variables.
Sensitive configuration files are excluded using .gitignore.
Local virtual environments are not committed to the repository.
Uploaded documents and local knowledge-base data should not be published to GitHub.
Authentication is implemented to manage user access and sessions.

Limitations

The quality of generated answers depends on the quality and content of the uploaded documents.
Very large or poorly formatted PDFs may require additional processing.
The system can only provide grounded answers from the indexed knowledge base.
API usage and response generation depend on the configured Gemini service.

Future Improvements

Potential future improvements include:
Support for additional document formats
Advanced document filtering
Improved metadata-based search
Streaming response
Evaluation metric for retrieval quality
More detailed usge analytics
Cloud-based storage for documents and indexes

Project Status

The application has been developed, tested locally, and containerized using Docker. The current version focuses on document ingestion, semantic retrieval, reranking, grounded question answering, authentication, and persistent conversations.
                    