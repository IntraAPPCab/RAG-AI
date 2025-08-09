import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from app.rag_pipeline import SmartRAG
from app.sql_pipeline import SQLPipeline
from app.router import Router
from app.settings import DATABASES

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()
rag = SmartRAG()
sql = SQLPipeline()
router = Router()
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

class Query(BaseModel):
    question: str
    source: str
    llm_choice: str

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    logger.debug("Accessing root endpoint")
    doc_names = list(rag.metadata.keys())
    db_names = list(DATABASES.keys())
    logger.debug(f"Doc names: {doc_names}, DB names: {db_names}")
    return templates.TemplateResponse("chat.html", {"request": request, "doc_names": doc_names, "db_names": db_names})

@app.post("/ask")
async def ask(query: Query):
    logger.debug(f"Received query: {query.question}, source: {query.source}, llm: {query.llm_choice}")
    try:
        if query.source == "automatico_docs":
            sources = router.choose_sources(query.question)
            logger.debug(f"Router selected sources: {sources}")
            results = []
            for src in sources:
                if src in DATABASES:
                    logger.debug(f"Querying SQL database: {src}")
                    results.append(sql.ask(query.question, src, query.llm_choice))
                else:
                    logger.debug(f"Querying document collection: {src}")
                    results.append(rag.query(query.question, src, query.llm_choice))
            return {"result": "\n".join(results)}
        elif query.source.startswith("doc:"):
            doc = query.source.split(":")[1]
            logger.debug(f"Querying specific document: {doc}")
            return {"result": rag.query(query.question, doc, query.llm_choice)}
        elif query.source.startswith("sql:"):
            db = query.source.split(":")[1]
            logger.debug(f"Querying specific database: {db}")
            return {"result": sql.ask(query.question, db, query.llm_choice)}
        else:
            logger.error(f"Invalid source: {query.source}")
            raise HTTPException(status_code=400, detail="Fuente inválida")
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")