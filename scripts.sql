create extension if not exists vector;
 CREATE TABLE IF NOT EXISTS documents (
         id SERIAL PRIMARY KEY,
         content TEXT NOT NULL,
         embedding VECTOR(5120) -- Adjust based on embedding model used
     );