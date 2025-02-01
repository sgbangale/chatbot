import os
import shutil
import numpy as np
import psycopg2
import ollama
from fastapi import FastAPI, UploadFile, File
from pdf2image import convert_from_path
from PIL import Image
import pytesseract

# Environment Variables for Database Connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:mysecretpassword@localhost:5432/rag_db")

# Database Connection
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

# Initialize FastAPI App
app = FastAPI()

# Create table if not exists
# cursor.execute("""
#     CREATE TABLE IF NOT EXISTS documents (
#         id SERIAL PRIMARY KEY,
#         content TEXT NOT NULL,
#         embedding VECTOR(1536) -- Adjust based on embedding model used
#     );
# """)
# conn.commit()

# Function to extract text from PDFs
def extract_text_from_pdf(pdf_path):
    images = convert_from_path(pdf_path)
    text = ""
    for image in images:
        text += pytesseract.image_to_string(image)
    return text

# Function to extract text from images
def extract_text_from_image(image_path):
    image = Image.open(image_path)
    return pytesseract.image_to_string(image)

# Function to generate text embeddings using Ollama
def get_embedding(text):
    response = ollama.embeddings(model="phi4", prompt=text)
    return response["embedding"]

# Function to store text and embeddings in PostgreSQL
def store_embedding(text, embedding):
    embedding_array = np.array(embedding)
    cursor.execute("INSERT INTO documents (content, embedding) VALUES (%s, %s)", (text, embedding_array.tolist()))
    conn.commit()

# Function to find the most relevant document using vector search
def find_relevant_document(query):
    query_embedding = get_embedding(query)
    query_embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"  # Convert to PostgreSQL vector format

    cursor.execute("""
        SELECT content, embedding <=> %s::vector AS distance
        FROM documents
        ORDER BY distance ASC
        LIMIT 1;
    """, (query_embedding_str,))
    
    result = cursor.fetchone()
    return result[0] if result else "No relevant document found."
# Function to generate responses using Ollama LLM
def answer_query(query):
    document = find_relevant_document(query)
    prompt = f"Using the following document, answer the question:\n\n{document}\n\nQuestion: {query}"
    
    response = ollama.chat(model="phi4", messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"]

# Health Check Endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy"}

# PDF Upload Endpoint
@app.post("/upload/pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    text = extract_text_from_pdf(file_path)
    embedding = get_embedding(text)
    print(f"Embedding size: {len(embedding)}")
    store_embedding(text, embedding)
    
    return {"message": "PDF processed successfully"}

# Image Upload Endpoint
@app.post("/upload/image/")
async def upload_image(file: UploadFile = File(...)):
    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    text = extract_text_from_image(file_path)
    embedding = get_embedding(text)
    store_embedding(text, embedding)
    
    return {"message": "Image processed successfully"}

# Query Endpoint to Get Answers
@app.get("/query/")
async def query_llm(question: str):
    response = answer_query(question)
    return {"response": response}