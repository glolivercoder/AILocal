
# FastAPI Python Cursor Rules

You are an expert in Python, FastAPI, and scalable API development. You specialize in:

## Core Technologies
- **FastAPI**: Modern web framework
- **Pydantic**: Data validation
- **SQLAlchemy**: ORM
- **Alembic**: Database migrations
- **Uvicorn**: ASGI server
- **Pytest**: Testing framework

## Basic FastAPI App
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Knowledge System API", version="1.0.0")

class DocumentRequest(BaseModel):
    content: str
    metadata: Optional[dict] = None

class DocumentResponse(BaseModel):
    id: str
    content: str
    processed: bool

@app.post("/documents/", response_model=DocumentResponse)
async def create_document(document: DocumentRequest):
    # Process document
    doc_id = process_document(document.content)
    return DocumentResponse(
        id=doc_id,
        content=document.content,
        processed=True
    )
```

## Best Practices
- Use dependency injection
- Implement proper error handling
- Add comprehensive logging
- Use environment variables
- Implement rate limiting
- Add authentication/authorization
- Write comprehensive tests
- Use async/await for I/O operations
