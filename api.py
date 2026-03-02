from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from retrieval.hybrid_search import hybrid_search


# -------------------------------------------------
# FastAPI App Initialization
# -------------------------------------------------

app = FastAPI(
    title="SHL Assessment Recommendation Engine",
    description="Enterprise RAG-based Assessment Recommendation System",
    version="6.0"
)

# Static + Templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# -------------------------------------------------
# Request Schema
# -------------------------------------------------

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5


# -------------------------------------------------
# Skill Dictionary
# -------------------------------------------------

COMMON_SKILLS = [
    "java", "python", "sql", "excel",
    "leadership", "communication", "collaboration",
    "sales", "data analysis", "personality",
    "cognitive", "management", "marketing",
    "consulting", "strategy", "finance",
    "operations", "analytics"
]


# -------------------------------------------------
# Skill Extraction
# -------------------------------------------------

def extract_skills(text):
    text = text.lower()
    found = []

    for skill in COMMON_SKILLS:
        if skill in text:
            found.append(skill)

    return found


# -------------------------------------------------
# Assessment Classification
# -------------------------------------------------

def classify_assessment(assessment):
    text = (assessment["name"] + " " + assessment["description"]).lower()

    if any(x in text for x in ["java", "python", "sql", "excel"]):
        return "Technical"

    if any(x in text for x in ["personality", "opq", "behavior"]):
        return "Personality"

    if any(x in text for x in ["cognitive", "ability", "reasoning"]):
        return "Cognitive"

    if any(x in text for x in ["simulation", "scenario"]):
        return "Simulation"

    return "General"


# -------------------------------------------------
# Reasoning + Confidence
# -------------------------------------------------

def generate_reasoning(query, assessment):

    query_skills = extract_skills(query)
    assessment_text = (assessment["name"] + " " + assessment["description"]).lower()

    matched_skills = []

    for skill in query_skills:
        if skill in assessment_text:
            matched_skills.append(skill)

    if matched_skills:
        confidence = min(0.6 + (0.1 * len(matched_skills)), 0.95)
        reason = f"Matches required skills: {', '.join(matched_skills)}."
    else:
        confidence = 0.5
        reason = "Recommended based on semantic similarity to job requirements."

    return reason, round(confidence, 2)


# -------------------------------------------------
# Bundle Generator
# -------------------------------------------------

def create_bundle(results):

    bundle = {
        "Technical": None,
        "Cognitive": None,
        "Personality": None
    }

    for r in results:
        category = classify_assessment(r)

        if category in bundle and bundle[category] is None:
            bundle[category] = {
                "name": r["name"],
                "url": r["url"]
            }

    # Remove empty categories
    bundle = {k: v for k, v in bundle.items() if v is not None}

    return bundle


# -------------------------------------------------
# Web UI Route
# -------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# -------------------------------------------------
# Recommendation API Endpoint
# -------------------------------------------------

@app.post("/recommend")
def recommend_assessments(request: QueryRequest):

    # Step 1: Retrieve top candidates
    results = hybrid_search(request.query, top_k=10)

    enriched_results = []

    # Step 2: Add reasoning, classification, confidence
    for r in results:

        reason, confidence = generate_reasoning(request.query, r)

        enriched_results.append({
            "name": r["name"],
            "url": r["url"],
            "description": r["description"],
            "assessment_type": classify_assessment(r),
            "confidence_score": confidence,
            "reason": reason
        })

    # Step 3: Create bundle
    bundle = create_bundle(results)

    return {
        "query": request.query,
        "recommended_bundle": bundle,
        "top_recommendations": enriched_results[:request.top_k]
    }