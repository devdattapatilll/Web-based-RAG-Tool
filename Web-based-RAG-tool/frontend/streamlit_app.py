"""
SHL Assessment Recommender — Streamlit Frontend

Premium dark-theme UI for querying the RAG-based assessment recommendation system.
"""

import json
import requests
import streamlit as st

# ─── Page Config ────────────────────────────────────────────────

st.set_page_config(
    page_title="SHL Assessment Recommender",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ─────────────────────────────────────────────────

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    * { font-family: 'Inter', sans-serif; }

    .stApp {
        background: linear-gradient(135deg, #0a0a1a 0%, #0d1117 50%, #0a0f1e 100%);
    }

    /* Hero Section */
    .hero {
        text-align: center;
        padding: 2rem 0 1rem 0;
    }
    .hero h1 {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #60a5fa, #a78bfa, #f472b6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.25rem;
        letter-spacing: -0.02em;
    }
    .hero p {
        color: #64748b;
        font-size: 1.05rem;
        font-weight: 400;
    }

    /* Search Box */
    .stTextArea textarea {
        background: #0f172a !important;
        border: 1px solid #1e293b !important;
        border-radius: 12px !important;
        color: #e2e8f0 !important;
        font-size: 0.95rem !important;
        padding: 1rem !important;
        transition: border-color 0.3s ease !important;
    }
    .stTextArea textarea:focus {
        border-color: #60a5fa !important;
        box-shadow: 0 0 0 3px rgba(96, 165, 250, 0.1) !important;
    }

    /* Results Counter */
    .results-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin: 1.5rem 0;
        padding: 0.75rem 1rem;
        background: linear-gradient(135deg, rgba(96,165,250,0.08), rgba(167,139,250,0.08));
        border-radius: 10px;
        border: 1px solid rgba(96,165,250,0.15);
    }
    .results-header span {
        color: #94a3b8;
        font-size: 0.95rem;
    }
    .results-header strong {
        color: #60a5fa;
        font-size: 1.1rem;
    }

    /* Assessment Card */
    .card {
        background: linear-gradient(145deg, #0f172a 0%, #131c2e 100%);
        border: 1px solid #1e293b;
        border-radius: 14px;
        padding: 1.75rem;
        margin-bottom: 1.25rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    .card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #60a5fa, #a78bfa, #f472b6);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    .card:hover {
        border-color: #334155;
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.3);
    }
    .card:hover::before {
        opacity: 1;
    }

    /* Card Header */
    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 1rem;
    }
    .card-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: #f1f5f9;
        margin: 0;
        line-height: 1.3;
    }
    .card-rank {
        color: #60a5fa;
        font-weight: 800;
        font-size: 1.1rem;
        margin-right: 0.5rem;
    }

    /* Badges */
    .badge-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin: 0.75rem 0;
    }
    .badge {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.3rem 0.7rem;
        border-radius: 6px;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.02em;
    }
    .badge-k {
        background: rgba(52, 211, 153, 0.12);
        color: #34d399;
        border: 1px solid rgba(52, 211, 153, 0.2);
    }
    .badge-p {
        background: rgba(251, 191, 36, 0.12);
        color: #fbbf24;
        border: 1px solid rgba(251, 191, 36, 0.2);
    }
    .badge-s {
        background: rgba(168, 85, 247, 0.12);
        color: #a855f7;
        border: 1px solid rgba(168, 85, 247, 0.2);
    }
    .badge-default {
        background: rgba(148, 163, 184, 0.1);
        color: #94a3b8;
        border: 1px solid rgba(148, 163, 184, 0.15);
    }

    /* Metadata Grid */
    .meta-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
        gap: 0.75rem;
        margin: 1rem 0;
    }
    .meta-item {
        padding: 0.6rem 0.8rem;
        background: rgba(15,23,42,0.6);
        border-radius: 8px;
        border: 1px solid #1e293b;
    }
    .meta-label {
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #475569;
        font-weight: 600;
        margin-bottom: 0.2rem;
    }
    .meta-value {
        color: #cbd5e1;
        font-size: 0.88rem;
        font-weight: 500;
    }

    /* Description */
    .card-desc {
        color: #94a3b8;
        font-size: 0.9rem;
        line-height: 1.65;
        margin-top: 0.75rem;
        padding-top: 0.75rem;
        border-top: 1px solid #1e293b;
    }

    /* Link */
    .card-link {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        color: #60a5fa;
        text-decoration: none;
        font-weight: 600;
        font-size: 0.85rem;
        transition: color 0.2s;
    }
    .card-link:hover {
        color: #93c5fd;
    }

    /* Sidebar */
    .sidebar-section {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 10px;
        padding: 1.25rem;
        margin-bottom: 1rem;
    }
    .sidebar-section h4 {
        color: #e2e8f0;
        margin-top: 0;
        font-size: 0.95rem;
    }

    /* Footer */
    .footer {
        text-align: center;
        color: #334155;
        font-size: 0.8rem;
        padding: 2rem 0 1rem 0;
        border-top: 1px solid #1e293b;
        margin-top: 3rem;
    }
</style>
""", unsafe_allow_html=True)

# ─── Header ─────────────────────────────────────────────────────

st.markdown("""
<div class="hero">
    <h1>🎯 SHL Assessment Recommender</h1>
    <p>AI-powered assessment matching using RAG &amp; Semantic Search</p>
</div>
""", unsafe_allow_html=True)

# ─── Sidebar ────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    
    api_url = st.text_input(
        "API Endpoint",
        value=st.session_state.get("api_url", "http://localhost:8000"),
        help="Backend API URL",
    )
    st.session_state.api_url = api_url
    
    st.markdown("---")
    
    st.markdown("""
    <div class="sidebar-section">
        <h4>📖 How It Works</h4>
        <ol style="color: #94a3b8; font-size: 0.85rem; padding-left: 1.2rem;">
            <li>Enter a job description or query</li>
            <li>System searches 389+ SHL assessments</li>
            <li>AI ranks and balances results</li>
            <li>Top 5-10 assessments returned</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="sidebar-section">
        <h4>💡 Example Queries</h4>
        <ul style="color: #94a3b8; font-size: 0.82rem; padding-left: 1.2rem;">
            <li>Java developer mid-level</li>
            <li>Entry-level customer service agent</li>
            <li>Senior data scientist with Python</li>
            <li>Sales manager leadership assessment</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="sidebar-section">
        <h4>🏷️ Test Type Legend</h4>
        <div style="font-size: 0.82rem;">
            <p style="color: #34d399; margin: 0.2rem 0;">● Knowledge & Skills</p>
            <p style="color: #fbbf24; margin: 0.2rem 0;">● Personality & Behavior</p>
            <p style="color: #a855f7; margin: 0.2rem 0;">● Simulation</p>
            <p style="color: #94a3b8; margin: 0.2rem 0;">● Other Types</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ─── Search Input ───────────────────────────────────────────────

query = st.text_area(
    "Enter job description or query",
    placeholder="e.g. 'I am hiring for Java developers who can work on core Java, multithreading, and Spring Boot'",
    height=100,
    label_visibility="collapsed",
)

col1, col2, col3 = st.columns([2, 1, 2])
with col1:
    search_btn = st.button("🔍 Find Assessments", type="primary", use_container_width=True)

# ─── Results ────────────────────────────────────────────────────

if search_btn and query.strip():
    with st.spinner("🔄 Searching 389+ assessments using hybrid RAG pipeline..."):
        try:
            response = requests.post(
                f"{api_url}/recommend",
                json={"query": query.strip()},
                timeout=120,
            )
            response.raise_for_status()
            data = response.json()
            
            assessments = data.get("recommended_assessments", [])
            
            if not assessments:
                st.warning("No matching assessments found. Try a different query.")
            else:
                st.markdown(f"""
                <div class="results-header">
                    <span>Found <strong>{len(assessments)}</strong> matching assessments</span>
                </div>
                """, unsafe_allow_html=True)
                
                for idx, item in enumerate(assessments, 1):
                    name = item.get("name", "Unknown")
                    url = item.get("url", "#")
                    description = item.get("description", "")
                    duration = item.get("duration")
                    adaptive = item.get("adaptive_support", "No")
                    remote = item.get("remote_support", "No")
                    test_types = item.get("test_type", [])
                    
                    # Build test type badges
                    badges_html = ""
                    for tt in test_types:
                        if "Knowledge" in tt or "Skill" in tt:
                            badges_html += f'<span class="badge badge-k">📚 {tt}</span>'
                        elif "Personality" in tt or "Behavior" in tt:
                            badges_html += f'<span class="badge badge-p">🧠 {tt}</span>'
                        elif "Simulation" in tt:
                            badges_html += f'<span class="badge badge-s">🖥️ {tt}</span>'
                        else:
                            badges_html += f'<span class="badge badge-default">{tt}</span>'
                    
                    duration_str = f"{duration} min" if duration else "Variable"
                    adaptive_icon = "✅" if adaptive == "Yes" else "—"
                    remote_icon = "✅" if remote == "Yes" else "—"
                    
                    st.markdown(f"""
                    <div class="card">
                        <div class="card-header">
                            <div>
                                <span class="card-rank">#{idx}</span>
                                <span class="card-title">{name}</span>
                            </div>
                            <a class="card-link" href="{url}" target="_blank">View Details →</a>
                        </div>
                        <div class="badge-row">{badges_html}</div>
                        <div class="meta-grid">
                            <div class="meta-item">
                                <div class="meta-label">Duration</div>
                                <div class="meta-value">⏱️ {duration_str}</div>
                            </div>
                            <div class="meta-item">
                                <div class="meta-label">Remote Testing</div>
                                <div class="meta-value">{remote_icon} {remote}</div>
                            </div>
                            <div class="meta-item">
                                <div class="meta-label">Adaptive/IRT</div>
                                <div class="meta-value">{adaptive_icon} {adaptive}</div>
                            </div>
                        </div>
                        <div class="card-desc">{description[:300]}{'...' if len(description) > 300 else ''}</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to the API. Make sure the backend is running.")
            st.info("Start the API with: `python main.py --api`")
        except Exception as e:
            st.error(f"Error: {str(e)}")

elif search_btn:
    st.warning("Please enter a query to search.")

# ─── Footer ─────────────────────────────────────────────────────

st.markdown("""
<div class="footer">
    SHL Assessment Recommender v2.0 · Powered by RAG + FAISS + BM25 · Built with ❤️
</div>
""", unsafe_allow_html=True)
