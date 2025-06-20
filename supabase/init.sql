
-- Configuração inicial do Supabase
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Schema para RAG
CREATE SCHEMA IF NOT EXISTS rag;

-- Tabela para documentos
CREATE TABLE IF NOT EXISTS rag.documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    filename TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB,
    embedding vector(384),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índice para busca por similaridade
CREATE INDEX IF NOT EXISTS documents_embedding_idx ON rag.documents USING ivfflat (embedding vector_cosine_ops);

-- Função para busca por similaridade
CREATE OR REPLACE FUNCTION rag.search_documents(
    query_embedding vector(384),
    match_threshold float DEFAULT 0.7,
    match_count int DEFAULT 5
)
RETURNS TABLE (
    id UUID,
    filename TEXT,
    content TEXT,
    metadata JSONB,
    similarity FLOAT
)
LANGUAGE SQL STABLE
AS $$
    SELECT
        documents.id,
        documents.filename,
        documents.content,
        documents.metadata,
        1 - (documents.embedding <=> query_embedding) AS similarity
    FROM rag.documents
    WHERE 1 - (documents.embedding <=> query_embedding) > match_threshold
    ORDER BY documents.embedding <=> query_embedding
    LIMIT match_count;
$$;
