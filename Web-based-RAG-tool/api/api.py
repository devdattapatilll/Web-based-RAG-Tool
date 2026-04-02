"""
FastAPI Backend — SHL Assessment Recommendation API

Endpoints:
  GET  /health     → Health check
  POST /recommend  → Get assessment recommendations
"""

import os
import sys
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from retriever.retrieval_pipeline import RetrievalPipeline

# Optional: Gemini LLM for query understanding
try:
    import google.generativeai as genai
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key and api_key != "your_google_api_key_here":
        genai.configure(api_key=api_key)
        llm = genai.GenerativeModel("gemini-2.0-flash")
        LLM_AVAILABLE = True
        print("Gemini LLM loaded successfully")
    else:
        llm = None
        LLM_AVAILABLE = False
        print("No API key found — LLM features disabled")
except Exception as e:
    llm = None
    LLM_AVAILABLE = False
    print(f"LLM not available: {e}")


# ─── Pydantic Models ────────────────────────────────────────────

class QueryRequest(BaseModel):
    query: str = Field(..., description="Natural language query or job description")


class AssessmentResponse(BaseModel):
    url: str
    name: str
    adaptive_support: str
    description: str
    duration: Optional[int]
    remote_support: str
    test_type: List[str]


class RecommendResponse(BaseModel):
    recommended_assessments: List[AssessmentResponse]


class HealthResponse(BaseModel):
    status: str


# ─── App Setup ──────────────────────────────────────────────────

app = FastAPI(
    title="SHL Assessment Recommender API",
    description="GenAI-powered RAG system for recommending SHL assessments",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize retrieval pipeline
pipeline = RetrievalPipeline()


# ─── Helper Functions ───────────────────────────────────────────

def extract_query_from_url(url: str) -> str:
    """Scrape job description text from a URL."""
    try:
        import requests
        from bs4 import BeautifulSoup
        
        response = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=15,
        )
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Try common JD containers
        for selector in [
            "div.job-description",
            "section.description",
            "div.posting-description",
            "article",
            "main",
        ]:
            container = soup.select_one(selector)
            if container:
                text = container.get_text(" ", strip=True)
                if len(text) > 50:
                    return text[:2000]
        
        # Fallback: get all paragraph text
        paragraphs = soup.find_all("p")
        text = " ".join(p.get_text(" ", strip=True) for p in paragraphs)
        return text[:2000] if text else url
        
    except Exception as e:
        print(f"URL scraping failed: {e}")
        return url


def enhance_query_with_llm(query: str) -> str:
    """Use LLM to extract key skills and intent from the query."""
    if not LLM_AVAILABLE or not llm:
        return query
    
    try:
        prompt = f"""Extract the key job requirements, skills, and assessment needs from this query.
Return a concise summary focusing on:
- Job role/title
- Required skills and competencies
- Seniority level
- Assessment type needed (cognitive, personality, technical)

Query: {query[:500]}

Return only the extracted keywords and requirements, nothing else."""
        
        response = llm.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,
                max_output_tokens=200,
            ),
        )
        enhanced = response.text.strip()
        # Combine original + enhanced for better retrieval
        return f"{query} {enhanced}"
    except Exception as e:
        print(f"LLM enhancement failed: {e}")
        return query


# ─── API Endpoints ──────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/recommend", response_model=RecommendResponse)
async def recommend(request: QueryRequest):
    """
    Get SHL assessment recommendations.
    
    Accepts a natural language query, job description, or URL.
    Returns 5-10 relevant assessments.
    """
    query = request.query.strip()
    
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    # If query is a URL, extract text from it
    if query.startswith(("http://", "https://")):
        query = extract_query_from_url(query)
    
    # Enhance query with LLM (optional)
    enhanced_query = enhance_query_with_llm(query)
    
    try:
        # Run retrieval pipeline
        results = pipeline.retrieve(
            query=enhanced_query,
            top_k=10,
            initial_k=20,
            balance_types=True,
        )
        
        # Ensure we return 5-10 results
        if len(results) < 5:
            # Retry without balancing if too few results
            results = pipeline.retrieve(
                query=enhanced_query,
                top_k=10,
                initial_k=30,
                balance_types=False,
            )
        
        results = results[:10]  # Cap at 10
        
        # Format response
        assessments = []
        for r in results:
            test_type = r.get("test_type", [])
            if isinstance(test_type, str):
                test_type = [test_type]
            
            assessments.append(
                AssessmentResponse(
                    url=r.get("url", ""),
                    name=r.get("name", "Unknown"),
                    adaptive_support=r.get("adaptive_support", "No"),
                    description=r.get("description", ""),
                    duration=r.get("duration"),
                    remote_support=r.get("remote_support", "No"),
                    test_type=test_type,
                )
            )
        
        return RecommendResponse(recommended_assessments=assessments)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retrieval error: {str(e)}")


# ─── Startup Event ──────────────────────────────────────────────

@app.on_event("startup")
async def startup():
    """Initialize the pipeline on startup."""
    try:
        pipeline.initialize()
        print("Pipeline initialized successfully")
    except Exception as e:
        print(f"Warning: Pipeline init failed: {e}")
        print("Pipeline will initialize on first request")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
