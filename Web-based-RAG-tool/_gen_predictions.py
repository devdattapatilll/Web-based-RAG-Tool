"""Generate devdatta_patil.csv from evaluation predictions."""
import csv
import os
import sys
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from retriever.retrieval_pipeline import RetrievalPipeline

def main():
    # Load dataset
    dataset_path = "data/dataset.xlsx"
    df = pd.read_excel(dataset_path)
    
    # Get unique queries
    queries = df["Query"].unique().tolist()
    
    # Init pipeline
    pipeline = RetrievalPipeline()
    pipeline.initialize()
    
    # Generate predictions
    predictions = []
    for query in queries:
        results = pipeline.retrieve(query=query, top_k=10, initial_k=20, balance_types=False)
        for r in results:
            predictions.append({
                "Query": query,
                "Assessment_url": r["url"]
            })
    
    # Save
    output_path = "devdatta_patil.csv"
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Query", "Assessment_url"])
        writer.writeheader()
        writer.writerows(predictions)
    
    print(f"Saved {len(predictions)} predictions to {output_path}")

if __name__ == "__main__":
    main()
