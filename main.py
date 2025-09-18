import os
import logging
import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from rag_pipeline import query_pipeline
from pathlib import Path

# Logging
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
LOGGER = logging.getLogger("drug_rag_api")

# App
app = FastAPI(title="Drug RAG API", version="1.0")

# Get the base directory
BASE_DIR = Path(__file__).parent

# Templates (for frontend)
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Serve static files
app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "static")),
    name="static"
)

# Add a route to serve the main page
@app.get("/test-static")
async def test_static():
    """Test endpoint to verify static files are being served"""
    static_dir = BASE_DIR / "static"
    return {
        "static_files_exist": {
            "styles.css": (static_dir / "styles.css").exists(),
            "script.js": (static_dir / "script.js").exists()
        },
        "static_dir": str(static_dir.absolute())
    }

@app.get("/")
async def read_root(request: Request):
    """Serve the main application page"""
    return templates.TemplateResponse("index.html", {"request": request})

# CORS
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
    final_answer: str

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

# API route for chat
@app.post("/query")
async def query_endpoint(request: Request):
    data = await request.json()
    query = data.get("query")
    if not query:
        raise HTTPException(status_code=400, detail="Query is required")
    
    # Process the query using your existing pipeline
    final_answer, _ = query_pipeline(query)
    return {"query": query, "answer": final_answer}

# Frontend route
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}   # only pass request
    )
