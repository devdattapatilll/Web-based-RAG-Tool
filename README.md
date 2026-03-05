# Web-based RAG Tool

[![Status](https://img.shields.io/badge/status-operational-brightgreen?style=for-the-badge)](https://img.shields.io/badge/status-operational-brightgreen)
[![Python](https://img.shields.io/badge/python-3.9+-blue?style=for-the-badge&logo=python)](https://img.shields.io/badge/python-3.9+-blue)
[![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)](https://img.shields.io/badge/license-MIT-green)

> **💡 Pro-Tip:** For the best visual experience with the Streamlit demo, please enable **Dark Mode** in your browser settings.

---

## 📖 Project Overview
**Web-based RAG Tool** is an AI-powered recommendation engine designed to automate the selection of SHL assessments for specific job roles. By utilizing **Retrieval-Augmented Generation (RAG)** and semantic search, it bridges the gap between complex job requirements and the ideal evaluation tools.

### 🚩 The Challenge
Aligning job descriptions with technical assessments often results in manual overhead and hiring mismatches. This tool solves that by providing context-aware matching in seconds.

### 🛠️ Our Approach
1. **Scrape:** Extracts data from SHL's product catalog.
2. **Embed:** Converts descriptions into high-dimensional vectors.
3. **Retrieve:** Performs semantic matching using **ChromaDB**.
4. **Augment:** Generates AI-driven HR insights via the **Gemini API**.
5. **API Deployment:** The tool is hosted and accessible via the [Render API Endpoint](https://shl-assessment-recommendor.onrender.com/recommend).

---

## 💻 Tech Stack

| Category | Tools & Technologies |
| :--- | :--- |
| **Backend** | `FastAPI`, `Uvicorn` |
| **AI/ML** | `ChromaDB`, `Sentence-Transformers`, `RAG` |
| **LLM** | `Google Gemini API` |
| **Frontend** | `Streamlit` |
| **Scraping** | `BeautifulSoup4`, `Requests` |
| **Cloud** | `Render`, `Streamlit Cloud` |

---

## ⚙️ How It Works (Pipeline)

1. **Data Collection:** Scrapes website details into structured JSON (`scraper.py`).
2. **Vector Store:** Descriptions are embedded and persisted in **ChromaDB** (`rag.py`).
3. **Processing:** Job descriptions are analyzed and ranked via the API (`api.py`).
4. **Intelligence:** Gemini API generates summaries on candidate levels and usage tips.
5. **Interface:** A clean Streamlit UI displays ranked matches with actionable insights.

---

## 📊 Workflow Diagram
```mermaid
graph TB
    Start([Start System]) --> Config[Initialize Configurations]
    
    subgraph Data_Preparation [DATA PREPARATION PHASE]
    Config --> Row1A[Scrape Website]
    Row1A --> Row1B[Clean Data]
    Row1B --> Row1C[Store JSON]
    Row1C --> Row2A[Generate Embeddings]
    Row2A --> Row2B[Store in ChromaDB]
    end
    
    subgraph Interaction [USER INTERACTION PHASE]
    Row2B --> Row3A[Receive Query]
    Row3A --> Row3B[Semantic Search]
    Row3B --> Row4A[Rank Top-N Matches]
    end
    
    subgraph AI_Insights [AI INSIGHTS PHASE]
    Row4A --> Row5A[Gemini API Analysis]
    Row5A --> End([Display Results])
    end

    %% High-Contrast Gold Styling for Visibility
    style Start fill:#FFD700,stroke:#000,stroke-width:2px,color:#000
    style End fill:#FFD700,stroke:#000,stroke-width:2px,color:#000
    style Config fill:#FFD700,stroke:#000,stroke-width:2px,color:#000
    style Row1A fill:#FFD700,stroke:#000,stroke-width:2px,color:#000
    style Row1B fill:#FFD700,stroke:#000,stroke-width:2px,color:#000
    style Row1C fill:#FFD700,stroke:#000,stroke-width:2px,color:#000
    style Row2A fill:#FFD700,stroke:#000,stroke-width:2px,color:#000
    style Row2B fill:#FFD700,stroke:#000,stroke-width:2px,color:#000
    style Row3A fill:#FFD700,stroke:#000,stroke-width:2px,color:#000
    style Row3B fill:#FFD700,stroke:#000,stroke-width:2px,color:#000
    style Row4A fill:#FFD700,stroke:#000,stroke-width:2px,color:#000
    style Row5A fill:#FFD700,stroke:#000,stroke-width:2px,color:#000

    %% Subgraph Container Styling
    style Data_Preparation fill:#222,stroke:#FFD700,stroke-width:2px,color:#FFD700
    style Interaction fill:#222,stroke:#FFD700,stroke-width:2px,color:#FFD700
    style AI_Insights fill:#222,stroke:#FFD700,stroke-width:2px,color:#FFD700
