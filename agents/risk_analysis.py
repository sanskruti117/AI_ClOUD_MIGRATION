"""
Module 4 — Risk Analysis Engine
Calculates migration risk score for each service.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from agents.dependency_graph import build_dependency_graph, get_downstream_dependencies
from agents.service_discovery import discover_dependencies
import os


CRITICALITY_WEIGHTS = {"critical": 1.0, "high": 0.8, "medium": 0.5, "low": 0.3}


def load_telemetry(telemetry_path: str = None) -> pd.DataFrame:
    """Load telemetry data."""
    if telemetry_path is None:
        telemetry_path = os.path.join(
            os.path.dirname(__file__), "..", "data", "telemetry_data.csv"
        )
    return pd.read_csv(telemetry_path)


def calculate_risk_scores(telemetry_path: str = None, df: pd.DataFrame = None) -> pd.DataFrame:
    """
    Calculate migration risk score for each service.
    Risk factors: dependencies, request volume, latency, CPU, error rate, criticality
    """
    if df is None:
        df = load_telemetry(telemetry_path)
    
    G = build_dependency_graph(discover_dependencies(df=df))
    
    # Aggregate metrics per service
    agg = df.groupby("service_name").agg({
        "request_volume": "mean",
        "request_latency": "mean",
        "cpu_usage": "mean",
        "memory_usage": "mean",
        "error_rate": "mean",
        "service_criticality": "first",
    }).reset_index()
    
    results = []
    for _, row in agg.iterrows():
        service = row["service_name"]
        
        # Dependency count (downstream = services this one calls)
        dep_count = len(get_downstream_dependencies(G, service))
        in_degree = G.in_degree(service)
        total_deps = dep_count + in_degree
        
        # Normalize factors (0-1 scale)
        dep_score = min(total_deps / 10, 1.0)
        volume_score = min(row["request_volume"] / 5000, 1.0)
        latency_score = min(row["request_latency"] / 500, 1.0)
        cpu_score = min(row["cpu_usage"] / 80, 1.0)
        error_score = min(row["error_rate"] * 50, 1.0)
        crit_score = CRITICALITY_WEIGHTS.get(row["service_criticality"], 0.5)
        
        # Weighted risk score (0-100)
        weights = {"dep": 0.25, "volume": 0.15, "latency": 0.15, "cpu": 0.1, "error": 0.2, "crit": 0.15}
        risk_score = (
            dep_score * weights["dep"] * 100 +
            volume_score * weights["volume"] * 100 +
            latency_score * weights["latency"] * 100 +
            cpu_score * weights["cpu"] * 100 +
            error_score * weights["error"] * 100 +
            crit_score * weights["crit"] * 100
        )
        risk_score = min(100, round(risk_score, 1))
        
        if risk_score >= 70:
            risk_level = "High"
        elif risk_score >= 40:
            risk_level = "Medium"
        else:
            risk_level = "Low"
        
        results.append({
            "service": service,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "dependency_count": total_deps,
            "request_volume": round(row["request_volume"], 0),
            "avg_latency_ms": round(row["request_latency"], 2),
            "cpu_usage_pct": round(row["cpu_usage"], 2),
            "error_rate": round(row["error_rate"], 4),
            "criticality": row["service_criticality"],
        })
    
    return pd.DataFrame(results).sort_values("risk_score", ascending=False)


if __name__ == "__main__":
    df = calculate_risk_scores()
    print(df[["service", "risk_score", "risk_level"]].to_string(index=False))
