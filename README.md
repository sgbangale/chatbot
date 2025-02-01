# Chatbot Project

This repository contains the code for a chatbot project using Retrieval-Augmented Generation (RAG).
This project implements a **Retrieval-Augmented Generation (RAG) system** using:
- **Ollama API** for LLM-based text generation
- **PostgreSQL + pgvector** for vector storage and similarity search
- **FastAPI** for serving API endpoints

## Getting Started

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/chatbot.git
    ```
2. Install the dependencies:
    ```sh
    pip install -r requirements.txt
    ```
3. Install Poppler (Required for PDF Processing)
    ```sh
    brew install poppler
    ```
4. Install Ollama
    ```sh
    curl -fsSL https://ollama.com/install.sh | sh
    ollama --version
    ollama pull phi4
    ```
5. Standup Postgress 
    ```sh
    docker-compose up --build -d
    ```
6. Run SQL scripts.sql
    ```sh
    docker exec -it postgres_db psql -U postgres -d rag_db
    ```
7. Run FAST API 
    ```sh
    uvicorn main:app --reload --port 8000
    ```
## Curls
```sh Upload pdf
curl --location 'http://localhost:8000/upload/pdf/' \
--form 'file=@"/path/to/somefile.pdf"'
```
```sh Query LLM
curl --location 'http://localhost:8000/query?question=xxx'
```