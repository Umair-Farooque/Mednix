import os
import logging
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from rag_pipeline import query_pipeline

# ------------------------------
# Logging
# ------------------------------
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
LOGGER = logging.getLogger("drug_rag_api")

# ------------------------------
# FastAPI App
# ------------------------------
app = FastAPI(title="Drug RAG API", version="1.0")

# ------------------------------
# Directories
# ------------------------------
BASE_DIR = Path(__file__).parent
static_dir = BASE_DIR / "static"
templates_dir = BASE_DIR / "templates"

# Ensure directories exist
static_dir.mkdir(exist_ok=True)
templates_dir.mkdir(exist_ok=True)

# ------------------------------
# Templates & Static Files
# ------------------------------
templates = Jinja2Templates(directory=str(templates_dir))
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# ------------------------------
# CORS
# ------------------------------
allowed = os.getenv("ALLOWED_ORIGINS", "")
origins = [o.strip() for o in allowed.split(",") if o.strip()] if allowed else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------
# Request / Response Models
# ------------------------------
class QueryRequest(BaseModel):
    query: str
    top_k: int = 3
    max_subqueries: int = 5

class QueryResponse(BaseModel):
    query: str
    final_answer: str

# ------------------------------
# Health Endpoints
# ------------------------------
@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.get("/readyz")
def readyz():
    return {"ready": True}

# ------------------------------
# Query API Endpoint
# ------------------------------
@app.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    if not request.query or not request.query.strip():
        raise HTTPException(status_code=400, detail="`query` must be a non-empty string.")

    LOGGER.info("Received query: %s", request.query[:200])
    final_answer, _ = query_pipeline(
        request.query,
        top_k=request.top_k,
        max_subqueries=request.max_subqueries
    )
    return {"query": request.query, "final_answer": final_answer}

# ------------------------------
# Frontend Route for Render
# ------------------------------
@app.get("/", response_class=HTMLResponse)
async def render_ui(request: Request):
    """
    Render the main index.html page for landing page on Render.
    """
    template_path = templates_dir / "index.html"
    if not template_path.exists():
        raise HTTPException(status_code=500, detail="Template not found")

    return templates.TemplateResponse(
        "index.html",
        {"request": request}  # only request is needed
    )
