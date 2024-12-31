from fastapi import FastAPI,  Form, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from src.qdrant_manager import QdrantManager
from fastapi.responses import HTMLResponse
from src.utils import format_bold_text

app = FastAPI()

qdrant = QdrantManager()

# Set up Jinja2 templates
templates = Jinja2Templates(directory="static")

# Mount static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/query", response_class=HTMLResponse)
async def query_page(request: Request):
    return templates.TemplateResponse("query.html", {"request": request})

@app.get("/ingest", response_class=HTMLResponse)
async def ingest(request: Request):
    return templates.TemplateResponse("ingest.html", {"request": request})

@app.post("/query", response_class=HTMLResponse)
async def handle_query(request: Request, user_query: str = Form(...)):
    # Process the query using QdrantManager
    result = qdrant.query(user_query)
    return templates.TemplateResponse(
        "query.html", {"request": request, "user_query": user_query, "result": format_bold_text(str(result))}
    )

@app.post("/ingest", response_class=HTMLResponse)
async def ingest(request: Request, pdf_file_name: str = Form(...)):
    result = qdrant.ingest_documents(pdf_file_name)

    try:
        return templates.TemplateResponse(
            "ingest.html", {"request": request, "result": result}
        )
    except Exception as e:
        return templates.TemplateResponse(
                    "ingest.html", {"request": request, "result": "Error ingesting docs"}
                )