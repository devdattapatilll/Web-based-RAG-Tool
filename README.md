# 🤖 Web-based RAG Tool (formerly TalentLens)

[![Status](https://img.shields.io/badge/status-operational-brightgreen?style=for-the-badge)](https://img.shields.io/badge/status-operational-brightgreen)
[![Python](https://img.shields.io/badge/python-3.9+-blue?style=for-the-badge&logo=python)](https://img.shields.io/badge/python-3.9+-blue)
[![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)](https://img.shields.io/badge/license-MIT-green)

> **💡 Pro-Tip:** For the best visual experience with the Streamlit demo, please enable **Dark Mode** in your browser settings.

---

## 🔗 Quick Access

| Resource | Link |
| :--- | :--- |
| 🚀 **Live Demo** | [Launch Streamlit App](https://talentlens-cimdbqsshfd37ja45o6mke.streamlit.app/) |
| 🔌 **API Endpoint** | [Render API](https://shl-assessment-recommendor.onrender.com/recommend) |
| 📺 **Walkthrough** | [Watch Demo Video](https://youtu.be/ocIS6QnSWcY) |

### 🎥 Project Preview
<p align="center">
  <a href="https://youtu.be/ocIS6QnSWcY">
    <img src="./ThumbnailVimeo.png" alt="Demo Preview" width="700" style="border-radius: 10px; shadow: 5px 5px 15px rgba(0,0,0,0.3);"/>
  </a>
</p>

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

1.  **Data Collection:** Scrapes website details into structured JSON (`scraper.py`).
2.  **Vector Store:** Descriptions are embedded and persisted in **ChromaDB** (`rag.py`).
3.  **Processing:** Job descriptions are analyzed and ranked via the API (`api.py`).
4.  **Intelligence:** Gemini API generates summaries on candidate levels and usage tips.
5.  **Interface:** A clean Streamlit UI displays ranked matches with actionable insights.

### 📊 Workflow Diagram
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

    style Start fill:#e1f5fe,stroke:#01579b
    style End fill:#ffebee,stroke:#b71c1c
    style Data_Preparation fill:#f3e5f5,stroke:#4a148c
    style Interaction fill:#e3f2fd,stroke:#0d47a1
    style AI_Insights fill:#fff3e0,stroke:#e65100
