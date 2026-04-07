"""
SHL Assessment Recommender — Main Entry Point

Usage:
  python main.py --setup       Convert data + build index
  python main.py --scrape      Scrape SHL catalog (takes ~30min)
  python main.py --evaluate    Run evaluation with dataset
  python main.py --compare     Baseline vs improved comparison
  python main.py --api         Start FastAPI server
  python main.py --frontend    Start Streamlit frontend
"""

import argparse
import os
import sys


def setup():
    """Convert existing scraped data and build FAISS index."""
    print("=" * 60)
    print("SETUP: Converting data and building index")
    print("=" * 60)
    
    # Step 1: Convert existing scraped data
    from scraper.scraper import convert_existing_data
    
    input_path = "data/shl_assessments_complete.json"
    output_path = "data/scraped_data.json"
    
    if os.path.exists(input_path):
        print(f"\nConverting existing data from {input_path}...")
        convert_existing_data(input_path, output_path)
    elif os.path.exists(output_path):
        print(f"\nScraped data already exists at {output_path}")
    else:
        print("ERROR: No scraped data found. Run --scrape first.")
        return
    
    # Step 2: Build FAISS index
    from embeddings.embedding_engine import EmbeddingEngine
    
    print("\nBuilding FAISS index...")
    engine = EmbeddingEngine()
    engine.build_index(output_path)
    
    print("\nSetup complete!")


def scrape():
    """Run the SHL catalog scraper."""
    from scraper.scraper import scrape_shl_catalog
    scrape_shl_catalog()


def evaluate():
    """Run evaluation module."""
    from evaluation.evaluate import evaluate_pipeline
    
    dataset_path = "data/dataset.xlsx"
    if not os.path.exists(dataset_path):
        # Try alternate locations
        for alt in [
            "Gen_AI Dataset (1).xlsx",
            "data/Gen_AI Dataset (1).xlsx",
        ]:
            if os.path.exists(alt):
                dataset_path = alt
                break
    
    evaluate_pipeline(dataset_path=dataset_path)


def compare():
    """Run baseline vs improved comparison."""
    from evaluation.evaluate import run_baseline_vs_improved
    
    dataset_path = "data/dataset.xlsx"
    if not os.path.exists(dataset_path):
        for alt in ["Gen_AI Dataset (1).xlsx", "data/Gen_AI Dataset (1).xlsx"]:
            if os.path.exists(alt):
                dataset_path = alt
                break
    
    run_baseline_vs_improved(dataset_path=dataset_path)


def start_api():
    """Start FastAPI server."""
    import uvicorn
    print("Starting API server on http://0.0.0.0:8000")
    print("Docs available at http://localhost:8000/docs")
    uvicorn.run("api.api:app", host="0.0.0.0", port=8000, reload=True)


def start_frontend():
    """Start Streamlit frontend."""
    os.system("streamlit run frontend/streamlit_app.py --server.port 8501")


def main():
    parser = argparse.ArgumentParser(
        description="SHL Assessment Recommender — RAG System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --setup       # First time setup
  python main.py --api         # Start API server
  python main.py --evaluate    # Run evaluation
  python main.py --compare     # Baseline vs improved
        """,
    )
    
    parser.add_argument("--setup", action="store_true", help="Convert data + build index")
    parser.add_argument("--scrape", action="store_true", help="Scrape SHL catalog")
    parser.add_argument("--evaluate", action="store_true", help="Run evaluation")
    parser.add_argument("--compare", action="store_true", help="Baseline vs improved")
    parser.add_argument("--api", action="store_true", help="Start API server")
    parser.add_argument("--frontend", action="store_true", help="Start Streamlit frontend")
    
    args = parser.parse_args()
    
    if args.setup:
        setup()
    elif args.scrape:
        scrape()
    elif args.evaluate:
        evaluate()
    elif args.compare:
        compare()
    elif args.api:
        start_api()
    elif args.frontend:
        start_frontend()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
