import os
import logging
import os
import os
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from rag_pipeline import query_pipeline

# Logging
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
LOGGER = logging.getLogger("drug_rag_api")

# App
app = FastAPI(title="Drug RAG API", version="1.0")

# Get the base directory
BASE_DIR = Path(__file__).parent

# Ensure static and templates directories exist
static_dir = BASE_DIR / "static"
templates_dir = BASE_DIR / "templates"

# Create directories if they don't exist
static_dir.mkdir(exist_ok=True)
templates_dir.mkdir(exist_ok=True)

# Templates (for frontend)
templates = Jinja2Templates(directory=str(templates_dir))

# Serve static files
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Add a route to serve the main page
@app.get("/test-static")
async def test_static():
    """Test endpoint to verify static files are being served"""
    static_dir = BASE_DIR / "static"
    css_path = static_dir / "styles.css"
    js_path = static_dir / "script.js"
    
    return {
        "static_files_exist": {
            "styles.css": css_path.exists(),
            "script.js": js_path.exists()
        },
        "static_dir": str(static_dir.absolute()),
        "files": {
            "styles.css": str(css_path.absolute()),
            "script.js": str(js_path.absolute())
        }
    }

@app.get("/test-css")
async def test_css():
    """Test endpoint to serve the CSS file directly"""
    css_path = static_dir / "styles.css"
    if not css_path.exists():
        raise HTTPException(status_code=404, detail="CSS file not found")
    return FileResponse(css_path)

@app.get("/test-js")
async def test_js():
    """Test endpoint to serve the JS file directly"""
    js_path = static_dir / "script.js"
    if not js_path.exists():
        raise HTTPException(status_code=404, detail="JS file not found")
    return FileResponse(js_path)

@app.get("/")
async def read_root(request: Request):
    """Serve the main application page"""
    # Check if the template exists
    template_path = templates_dir / "index.html"
    if not template_path.exists():
        raise HTTPException(status_code=500, detail="Template not found")
    
    # Serve the template
    return templates.TemplateResponse("index.html", {
        "request": request,
        "static_url": "/static"
    })

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
