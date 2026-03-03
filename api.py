from fastapi import FastAPI
from pydantic import BaseModel
import traceback

app = FastAPI(
    title="SHL Assessment Recommendation Engine",
    version="6.0"
)

# -------------------------------------------------
# Lazy Load Hybrid Search
# -------------------------------------------------

hybrid_model = None

def load_model():
    global hybrid_model
    if hybrid_model is None:
        from retrieval.hybrid_search import hybrid_search
        hybrid_model = hybrid_search
    return hybrid_model


# -------------------------------------------------
# Request Schema
# -------------------------------------------------

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5


# -------------------------------------------------
# Health Check Endpoint
# -------------------------------------------------

@app.get("/")
def health():
    return {"status": "API running successfully"}


# -------------------------------------------------
# Recommendation Endpoint
# -------------------------------------------------

@app.post("/recommend")
def recommend(request: QueryRequest):
    try:
        hybrid_search = load_model()
        results = hybrid_search(request.query, top_k=request.top_k)

        return {
            "query": request.query,
            "recommendations": results
        }

    except Exception as e:
        return {
            "error": str(e),
            "trace": traceback.format_exc()
        }