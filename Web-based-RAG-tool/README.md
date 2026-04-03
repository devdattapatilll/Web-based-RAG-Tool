# SHL Assessment Recommender 🎯

A production-ready, GenAI-powered **Retrieval-Augmented Generation (RAG)** web application for recommending SHL assessments based on natural language queries or job descriptions.

---

## 🔗 Live Links

| Resource | URL |
|----------|-----|
| **Live Web App** | [shl-assessment-recommender.streamlit.app](https://shl-assessment1-devdattapatilll.streamlit.app/) |
| **API Endpoint** | [shl-assessment-api.onrender.com](https://shl-assessment1.onrender.com/) |
| **API Docs (Swagger)** | [shl-assessment-api.onrender.com/docs](https://shl-assessment1.onrender.com/docs) |
| **GitHub Repository** | [github.com/devdattapatilll/SHL-assessment1](https://github.com/devdattapatilll/SHL-assessment1) |

### API Usage

```bash
# Health check
curl https://shl-assessment1.onrender.com/health

# Get recommendations
curl -X POST https://shl-assessment1.onrender.com/recommend \
  -H "Content-Type: application/json" \
  -d '{"query": "I need a test for Java developers with 3 years experience"}'
```

**Response Format:**
```json
{
  "recommended_assessments": [
    {
      "url": "https://www.shl.com/...",
      "name": "Java 8 (New)",
      "adaptive_support": "No",
      "description": "Multi-choice test measuring...",
      "duration": 40,
      "remote_support": "Yes",
      "test_type": ["Knowledge & Skills"]
    }
  ]
}
```

---

## 🌟 Key Features

- **Full Catalog Scraper**: Dynamically scrapes 389+ Individual Test Solutions from SHL's product catalog
- **Hybrid RAG Pipeline**: FAISS dense retrieval + BM25 sparse retrieval fused via Reciprocal Rank Fusion (RRF)
- **Balanced Recommendations**: Intelligently balances "Knowledge & Skills" and "Personality & Behavior" assessments
- **LLM Query Enhancement**: Optional Google Gemini integration for extracting skills/intent from vague queries
- **Premium Frontend**: Modern dark-themed Streamlit UI with gradient cards and metadata badges
- **Comprehensive Evaluation**: Automated Mean Recall@10 computation against ground-truth dataset

## 🏛️ Architecture

```
Query → [Optional LLM Enhancement] → Hybrid Search
                                        ├── FAISS Semantic (Top-20)
                                        └── BM25 Keyword (Top-20)
                                              ↓
                                    Reciprocal Rank Fusion (70/30)
                                              ↓
                                    K/P Type Balancing
                                              ↓
                                    Top 5-10 Recommendations
```

## 📊 Evaluation Results

| Configuration | Mean Recall@10 |
|--------------|----------------|
| Baseline (FAISS only) | 0.02 |
| **Hybrid (FAISS + BM25 + RRF)** | **0.17** |

**8.5× improvement** over baseline through hybrid search.

## 🚀 Quick Start (Local)

```bash
# Install dependencies
pip install -r requirements.txt

# Setup: convert data + build FAISS index
python main.py --setup

# Start API server (http://localhost:8000)
python main.py --api

# Start Streamlit UI (http://localhost:8501)
python main.py --frontend

# Run evaluation
python main.py --evaluate
```

## 📂 Project Structure

```
Web-based-RAG-tool/
├── scraper/          # SHL catalog web scraper
├── embeddings/       # FAISS index + sentence-transformers
├── retriever/        # Hybrid RAG pipeline (FAISS + BM25 + RRF)
├── api/              # FastAPI backend (/health, /recommend)
├── frontend/         # Streamlit UI (self-contained)
├── evaluation/       # Recall@10 metrics + CSV export
├── data/             # Scraped data, FAISS index, predictions
├── main.py           # CLI entry point
└── requirements.txt  # Dependencies
```

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Embeddings | `all-MiniLM-L6-v2` (Sentence-Transformers) |
| Vector Store | FAISS (CPU, Inner Product) |
| Keyword Search | BM25/Okapi |
| Fusion | Reciprocal Rank Fusion (k=60) |
| API | FastAPI + Uvicorn |
| Frontend | Streamlit |
| LLM (optional) | Google Gemini 2.0 Flash |
