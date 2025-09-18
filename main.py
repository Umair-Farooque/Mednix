import os
import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from rag_pipeline import query_pipeline

# Logging
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
LOGGER = logging.getLogger("drug_rag_api")

# App
app = FastAPI(title="Drug RAG API", version="1.0")

# Serve static files (CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates (for frontend)
templates = Jinja2Templates(directory="templates")

# CORS (API only – frontend served directly from same origin)
allowed = os.getenv("ALLOWED_ORIGINS", "")
if allowed:
    origins = [o.strip() for o in allowed.split(",") if o.strip()]
else:
    origins = ["*"]  # development only

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request / Response models
class QueryRequest(BaseModel):
    query: str
    top_k: int = 3
    max_subqueries: int = 5

class QueryResponse(BaseModel):
    query: str
    final_answer: str  # removed sub_answers

# Health endpoints
@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.get("/readyz")
def readyz():
    return {"ready": True}

# Query API
@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    if not request.query or not request.query.strip():
        raise HTTPException(status_code=400, detail="`query` must be a non-empty string.")

    LOGGER.info("Received query: %s", request.query[:200])
    final_answer, _ = query_pipeline(
        request.query, 
        top_k=request.top_k, 
        max_subqueries=request.max_subqueries
    )
    return {"query": request.query, "final_answer": final_answer}

# Frontend route
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})