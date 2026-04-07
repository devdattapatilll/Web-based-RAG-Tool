import streamlit as st
import requests
from streamlit_lottie import st_lottie
import json

# Config
st.set_page_config(
    page_title="AI Assessment Engine",
    layout="wide",
    page_icon="⚡",
    initial_sidebar_state="expanded"
)

# Custom CSS for Modern Minimalist Tech Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    * {
        font-family: 'Inter', sans-serif;
    }

    .main-title {
        color: #f8fafc;
        font-size: 2.75rem;
        font-weight: 800;
        margin-bottom: 0.25rem;
        letter-spacing: -0.025em;
    }
    
    .sub-title {
        color: #0ea5e9;
        font-size: 1.15rem;
        font-weight: 500;
        margin-top: 0;
        margin-bottom: 2rem;
    }

    .assessment-card {
        border-radius: 8px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        background-color: #0f172a;
        border: 1px solid #1e293b;
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
    }

    .assessment-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 25px -5px rgba(14, 165, 233, 0.15);
        border-color: #0ea5e9;
    }

    .assessment-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: #f1f5f9;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }

    .relevance-badge {
        background-color: rgba(16, 185, 129, 0.1);
        color: #34d399;
        padding: 0.35rem 0.85rem;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.9rem;
        border: 1px solid rgba(52, 211, 153, 0.2);
        display: inline-block;
    }

    .detail-row {
        display: flex;
        align-items: center;
        padding: 0.65rem 0;
        border-bottom: 1px dashed #1e293b;
    }

    .detail-row:last-child {
        border-bottom: none;
    }

    .detail-label {
        font-weight: 500;
        color: #64748b;
        min-width: 150px;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .detail-value {
        color: #e2e8f0;
        font-size: 0.95rem;
        flex: 1;
    }

    .ai-insights {
        background-color: #0b1120;
        padding: 1.25rem;
        border-radius: 6px;
        margin-top: 1.5rem;
        border-left: 3px solid #0ea5e9;
    }

    .ai-insights-header {
        color: #38bdf8;
        font-weight: 600;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .ai-insights ul {
        margin: 0;
        padding-left: 1.25rem;
    }

    .ai-insights li {
        margin: 0.35rem 0;
        color: #94a3b8;
        font-size: 0.95rem;
        line-height: 1.5;
    }

    .info-card {
        background-color: #0f172a;
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid #1e293b;
    }

    .info-card h3 {
        color: #f8fafc;
        margin-top: 0;
        font-size: 1.1rem;
    }

    .code-box {
        background-color: #020617;
        padding: 1rem;
        border-radius: 6px;
        margin: 0.5rem 0;
        font-family: 'JetBrains Mono', 'Courier New', monospace;
        font-size: 0.85rem;
        color: #cbd5e0;
        border: 1px solid #1e293b;
    }

    .code-box span.highlight {
        color: #38bdf8;
    }

    .divider-line {
        height: 1px;
        background-color: #1e293b;
        margin: 2rem 0;
    }
    
    .assessment-description {
        color: #94a3b8;
        font-size: 0.95rem;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-title">⚡ Web-based RAG Tool</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Powered by Semantic Search & LLM Inference</div>', unsafe_allow_html=True)

# Instructions Section
with st.expander("ℹ️ System Documentation & Usage Guide", expanded=False):
    st.markdown("""
    <div class="info-card">
        <h3>🔍 Operational Overview</h3>
        <p style="color: #94a3b8; font-size: 0.95rem;">Enter a role description or standard job posting. The Retrieval-Augmented Generation (RAG) pipeline will cross-reference the query against our vector database to surface the highest-probability assessment matches.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="info-card">
            <h3>⚙️ Query Parameters</h3>
            <ul style="color: #94a3b8; font-size: 0.9rem; padding-left: 1.2rem;">
                <li><strong>Seniority Level:</strong> Specify Entry, Mid, or Senior.</li>
                <li><strong>Tech Stack/Skills:</strong> List core competencies.</li>
                <li><strong>Domain:</strong> Note the industry (e.g., FinTech, Healthcare).</li>
                <li><strong>URL Parsing:</strong> Direct job links are supported.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-card">
            <h3>💡 Test Queries</h3>
            <div class="code-box">
                <span class="highlight">Query 1:</span> "Senior Data Scientist proficient in PyTorch and predictive modeling"
            </div>
            <div class="code-box">
                <span class="highlight">Query 2:</span> "Entry-level technical support specialist, excellent communication"
            </div>
        </div>
        """, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown('<h2 style="color: #f8fafc; margin-bottom: 1.5rem;">Control Panel</h2>', unsafe_allow_html=True)
    
    use_ai = st.toggle("🧠 Enable LLM Insights", value=True)

    with st.expander("Network Configuration"):
        api_endpoint = st.text_input(
            "Inference API Endpoint",
            value=st.session_state.get('api_url', "https://talentlens-gdmn.onrender.com/recommend"),
            help="Configure the backend connection for the RAG pipeline."
        )
        if api_endpoint:
            st.session_state.api_url = api_endpoint

    st.markdown('<div class="divider-line"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="background-color: #0f172a; padding: 1rem; border-radius: 6px; border: 1px solid #1e293b;">
        <h4 style="color: #e2e8f0; margin-top: 0; font-size: 0.95rem;">Metrics Legend</h4>
        <div style="color: #94a3b8; font-size: 0.85rem;">
            <p style="margin-bottom: 0.5rem;"><strong>Distance Score:</strong> Values closer to 0.0 indicate higher semantic similarity in vector space.</p>
            <p style="margin-bottom: 0.2rem;">🟢 Native Support</p>
            <p style="margin-bottom: 0.2rem;">🔴 No Support</p>
            <p style="margin-bottom: 0;">❓ Data Unavailable</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Initialize api_url from session state
api_url = st.session_state.get('api_url', "https://talentlens-gdmn.onrender.com/recommend")

# Main Content Search
st.markdown('<div style="margin: 2rem 0 1rem 0; font-weight: 600; color: #e2e8f0;">Input Target Profile:</div>', unsafe_allow_html=True)
query = st.text_input(
    "Search",
    placeholder="e.g. 'Cloud Architect with AWS and Kubernetes experience'",
    label_visibility="collapsed"
)

col1, col2, col3 = st.columns([1.5, 1, 2])
with col1:
    search_button = st.button("Run Pipeline", type="primary", use_container_width=True)

if search_button and query:
    with st.spinner("Processing embeddings and querying vector store..."):
        try:
            api_response = requests.post(
                api_url,
                json={"text": query, "use_ai": use_ai},
                timeout=120
            )
            api_response.raise_for_status()
            response = api_response.json()

            if not response:
                st.warning("⚠️ Query returned no confident matches. Adjust parameters and retry.")
            else:
                st.markdown(f'<div style="color: #0ea5e9; font-weight: 600; font-size: 1.1rem; margin: 2rem 0 1.5rem 0;">Successfully retrieved {len(response)} optimized matches</div>', unsafe_allow_html=True)

                for idx, item in enumerate(sorted(response, key=lambda x: x['score']), 1):
                    # Data Extraction
                    name = item.get('name', 'Unknown Assessment')
                    url = item.get('url', '#')
                    score = item.get('score', 1.0)
                    duration = item.get('duration', 'Unspecified')
                    languages = ', '.join(item.get('languages', [])) or 'Unspecified'
                    job_level = item.get('job_level', 'Unspecified')
                    remote_testing = item.get('remote_testing', '❓')
                    adaptive_support = item.get('adaptive_support', item.get('adaptive/irt_support', '❓'))
                    test_type = item.get('test_type', 'Unspecified')
                    description = item.get('description', 'Data unavailable.')
                    ai_insights = item.get('ai_insights', '') if use_ai else ''

                    # Render UI Card
                    with st.container():
                        st.markdown('<div class="assessment-card">', unsafe_allow_html=True)

                        col_head1, col_head2 = st.columns([4, 1])
                        with col_head1:
                            st.markdown(f'<h2 class="assessment-title"><span style="color: #38bdf8;">{idx}.</span> {name}</h2>', unsafe_allow_html=True)
                        with col_head2:
                            st.markdown(f'<div style="text-align: right;"><span class="relevance-badge">Score: {score:.4f}</span></div>', unsafe_allow_html=True)

                        st.markdown('<div style="margin-top: 1.5rem;"></div>', unsafe_allow_html=True)

                        st.markdown(f'''
                        <div class="detail-row">
                            <span class="detail-label">Documentation</span>
                            <span class="detail-value"><a href="{url}" target="_blank" style="color: #38bdf8; text-decoration: none; font-weight: 500;">Access Specs ↗</a></span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Time Allocation</span>
                            <span class="detail-value">{duration}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Localization</span>
                            <span class="detail-value">{languages}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Target Level</span>
                            <span class="detail-value">{job_level}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Remote Capable</span>
                            <span class="detail-value">{remote_testing}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">IRT/Adaptive</span>
                            <span class="detail-value">{adaptive_support}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Category</span>
                            <span class="detail-value">{test_type}</span>
                        </div>
                        ''', unsafe_allow_html=True)

                        st.markdown('<div style="margin-top: 1.5rem; padding-top: 1rem; border-top: 1px dashed #1e293b;">', unsafe_allow_html=True)
                        st.markdown('<div style="color: #e2e8f0; font-weight: 600; font-size: 0.95rem; margin-bottom: 0.5rem;">Synopsis</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="assessment-description">{description}</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)

                        if ai_insights:
                            st.markdown('<div class="ai-insights">', unsafe_allow_html=True)
                            st.markdown('<div class="ai-insights-header"><span>🧠</span> LLM Inference Output</div>', unsafe_allow_html=True)
                            insight_html = '<ul>'
                            for line in ai_insights.split('\n'):
                                if line.strip():
                                    insight_html += f'<li>{line.strip()}</li>'
                            insight_html += '</ul>'
                            st.markdown(insight_html, unsafe_allow_html=True)
                            st.markdown('</div>', unsafe_allow_html=True)

                        st.markdown('</div>', unsafe_allow_html=True)
                        
        except Exception as e:
            st.error(f"⚠️ Runtime Exception: {str(e)}")
            st.info("Verify the inference API endpoint is actively accepting connections.")

# Footer
st.markdown('<div class="divider-line"></div>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #64748b; font-size: 0.85rem; font-family: monospace;">System Build: Web-based RAG Tool v1.0 | Engine Operational</p>', unsafe_allow_html=True)