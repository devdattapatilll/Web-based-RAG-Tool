"""
Evaluation Module — Computes Mean Recall@10 using the provided dataset.

Steps:
  1. Load dataset (Excel) with queries and ground truth URLs
  2. For each query, run the recommendation pipeline
  3. Compare predicted URLs vs ground truth URLs
  4. Compute Recall@K for each query
  5. Compute Mean Recall@10 across all queries
  6. Generate CSV predictions file
"""

import csv
import json
import os
import sys
import time
from typing import Dict, List, Tuple
from urllib.parse import urlparse

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from retriever.retrieval_pipeline import RetrievalPipeline


def normalize_url(url: str) -> str:
    """Normalize URL by extracting just the final slug for robust comparison."""
    url = str(url).strip().lower().rstrip("/")
    # Extract the last part of the URL (the slug)
    slug = url.split("/")[-1]
    return slug


def load_dataset(path: str) -> Dict[str, List[str]]:
    """
    Load the evaluation dataset from Excel.
    
    Returns dict: {query: [list of ground truth URLs]}
    """
    df = pd.read_excel(path)
    
    dataset = {}
    for _, row in df.iterrows():
        query = str(row["Query"]).strip()
        url = str(row["Assessment_url"]).strip()
        
        if query not in dataset:
            dataset[query] = []
        dataset[query].append(normalize_url(url))
    
    return dataset


def compute_recall_at_k(
    predicted_urls: List[str],
    ground_truth_urls: List[str],
    k: int = 10,
) -> float:
    """
    Compute Recall@K for a single query.
    
    Recall@K = |relevant results in top K| / |total relevant results|
    """
    if not ground_truth_urls:
        return 0.0
    
    # Normalize all URLs
    predicted_normalized = [normalize_url(u) for u in predicted_urls[:k]]
    truth_normalized = [normalize_url(u) for u in ground_truth_urls]
    
    # Count hits
    hits = sum(1 for url in predicted_normalized if url in truth_normalized)
    
    recall = hits / len(truth_normalized)
    return recall


def evaluate_pipeline(
    dataset_path: str = "data/dataset.xlsx",
    output_path: str = "data/evaluation_results.json",
    csv_output_path: str = "data/predictions.csv",
    k: int = 10,
) -> Dict:
    """
    Run full evaluation of the retrieval pipeline.
    
    Returns evaluation results including Mean Recall@K.
    """
    print("=" * 60)
    print("SHL Assessment Recommender — Evaluation")
    print("=" * 60)
    
    # Load dataset
    print(f"\nLoading dataset from {dataset_path}...")
    dataset = load_dataset(dataset_path)
    print(f"Loaded {len(dataset)} unique queries with ground truth URLs")
    
    # Initialize pipeline
    print("\nInitializing retrieval pipeline...")
    pipeline = RetrievalPipeline()
    pipeline.initialize()
    
    # Run evaluation
    results = []
    all_predictions = []
    query_recalls = []
    
    print(f"\nEvaluating {len(dataset)} queries...")
    print("-" * 60)
    
    for i, (query, truth_urls) in enumerate(dataset.items(), 1):
        print(f"\n[{i}/{len(dataset)}] Query: {query[:80]}...")
        print(f"  Ground truth URLs: {len(truth_urls)}")
        
        # Get predictions
        try:
            predicted = pipeline.retrieve(
                query=query,
                top_k=k,
                initial_k=20,
                balance_types=False,  # Don't balance for evaluation
            )
            predicted_urls = [r["url"] for r in predicted]
        except Exception as e:
            print(f"  ERROR: {e}")
            predicted_urls = []
            predicted = []
        
        # Compute Recall@K
        recall = compute_recall_at_k(predicted_urls, truth_urls, k=k)
        query_recalls.append(recall)
        
        print(f"  Predicted URLs: {len(predicted_urls)}")
        print(f"  Recall@{k}: {recall:.4f}")
        
        # Store results
        results.append({
            "query": query,
            "ground_truth_urls": truth_urls,
            "predicted_urls": predicted_urls,
            "recall_at_k": recall,
            "num_ground_truth": len(truth_urls),
            "num_predicted": len(predicted_urls),
        })
        
        # Store predictions for CSV
        for url in predicted_urls:
            all_predictions.append({"Query": query, "Assessment_url": url})
    
    # Compute Mean Recall@K
    mean_recall = sum(query_recalls) / len(query_recalls) if query_recalls else 0.0
    
    print("\n" + "=" * 60)
    print(f"EVALUATION RESULTS")
    print("=" * 60)
    print(f"Total queries evaluated: {len(dataset)}")
    print(f"Mean Recall@{k}: {mean_recall:.4f}")
    print(f"Min Recall@{k}:  {min(query_recalls):.4f}")
    print(f"Max Recall@{k}:  {max(query_recalls):.4f}")
    
    # Count queries with perfect recall
    perfect = sum(1 for r in query_recalls if r >= 1.0)
    partial = sum(1 for r in query_recalls if 0 < r < 1.0)
    zero = sum(1 for r in query_recalls if r == 0.0)
    print(f"\nPerfect recall (1.0):  {perfect}/{len(dataset)}")
    print(f"Partial recall (>0):  {partial}/{len(dataset)}")
    print(f"Zero recall (0.0):    {zero}/{len(dataset)}")
    
    # Save evaluation results
    eval_output = {
        "mean_recall_at_k": mean_recall,
        "k": k,
        "num_queries": len(dataset),
        "min_recall": min(query_recalls) if query_recalls else 0,
        "max_recall": max(query_recalls) if query_recalls else 0,
        "perfect_recall_count": perfect,
        "partial_recall_count": partial,
        "zero_recall_count": zero,
        "per_query_results": results,
    }
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(eval_output, f, indent=2, ensure_ascii=False)
    print(f"\nDetailed results saved to {output_path}")
    
    # Save CSV predictions
    _save_predictions_csv(all_predictions, csv_output_path)
    
    return eval_output


def _save_predictions_csv(
    predictions: List[Dict],
    output_path: str = "data/predictions.csv",
) -> None:
    """Save predictions in the required CSV format."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Query", "Assessment_url"])
        writer.writeheader()
        writer.writerows(predictions)
    
    print(f"Predictions CSV saved to {output_path} ({len(predictions)} rows)")


def run_baseline_vs_improved(
    dataset_path: str = "data/dataset.xlsx",
) -> None:
    """
    Run comparison between baseline (vector-only) and improved (hybrid) pipeline.
    Logs performance before and after improvement.
    """
    print("\n" + "=" * 60)
    print("BASELINE vs IMPROVED COMPARISON")
    print("=" * 60)
    
    dataset = load_dataset(dataset_path)
    pipeline = RetrievalPipeline()
    pipeline.initialize()
    
    # Baseline: vector search only (no BM25, no balancing)
    print("\n--- BASELINE: Vector Search Only ---")
    baseline_recalls = []
    for query, truth_urls in dataset.items():
        predicted = pipeline.engine.search(query, top_k=10)
        predicted_urls = [r[0]["url"] for r in predicted]
        recall = compute_recall_at_k(predicted_urls, truth_urls, k=10)
        baseline_recalls.append(recall)
    
    baseline_mean = sum(baseline_recalls) / len(baseline_recalls)
    print(f"Baseline Mean Recall@10: {baseline_mean:.4f}")
    
    # Improved: hybrid search with re-ranking
    print("\n--- IMPROVED: Hybrid Search + Re-ranking ---")
    improved_recalls = []
    for query, truth_urls in dataset.items():
        predicted = pipeline.retrieve(
            query=query, top_k=10, initial_k=20, balance_types=False
        )
        predicted_urls = [r["url"] for r in predicted]
        recall = compute_recall_at_k(predicted_urls, truth_urls, k=10)
        improved_recalls.append(recall)
    
    improved_mean = sum(improved_recalls) / len(improved_recalls)
    print(f"Improved Mean Recall@10: {improved_mean:.4f}")
    
    # Summary
    delta = improved_mean - baseline_mean
    print(f"\n--- IMPROVEMENT ---")
    print(f"Baseline:  {baseline_mean:.4f}")
    print(f"Improved:  {improved_mean:.4f}")
    print(f"Delta:     {delta:+.4f} ({delta/max(baseline_mean,0.001)*100:+.1f}%)")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Evaluate SHL Recommender")
    parser.add_argument("--dataset", default="data/dataset.xlsx", help="Path to dataset")
    parser.add_argument("--compare", action="store_true", help="Run baseline vs improved")
    args = parser.parse_args()
    
    if args.compare:
        run_baseline_vs_improved(args.dataset)
    else:
        evaluate_pipeline(dataset_path=args.dataset)
