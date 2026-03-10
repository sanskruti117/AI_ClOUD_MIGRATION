"""
Module 9 — Interactive Streamlit Dashboard
AI Cloud Migration Copilot - Hackathon Demo
"""

import sys
import os

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
os.chdir(PROJECT_ROOT)

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
from datetime import datetime

# Import project modules
from data.telemetry_generator import generate_telemetry_data
from agents.service_discovery import discover_dependencies, format_dependency_output
from agents.dependency_graph import build_dependency_graph, graph_to_plotly_data, get_graph_metrics
from agents.risk_analysis import calculate_risk_scores
from agents.migration_planner import get_migration_order, format_migration_plan
from simulation.migration_simulator import compare_strategies, get_recommended_plan
from cost.cost_estimator import estimate_cloud_cost, get_total_estimated_cost
from utils.failure_predictor import get_failure_predictions
from utils.ai_assistant import answer_question, get_context_data
from utils.data_loader import normalize_external_csv, validate_uploaded_data

# Add PyVis and streamlit components imports
from pyvis.network import Network
import streamlit.components.v1 as components

# Page config
st.set_page_config(
    page_title="AI Cloud Migration Copilot",
    page_icon="☁️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for modern gradient UI theme
st.markdown(
    """
<style>
    /* Global Styles */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 35%, #24243e 100%);
        color: #ffffff;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        min-height: 100vh;
    }

    /* Hero Section */
    .main-header {
        font-size: 3.5rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 50%, #06b6d4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
        line-height: 1.1;
    }

    .sub-header {
        text-align: center;
        color: #e0e7ff;
        margin-bottom: 2rem;
        font-size: 1.1rem;
        font-weight: 400;
        opacity: 0.9;
    }

    /* KPI Cards - Modern AI Dashboard Style */
    .kpi-row {
        margin-bottom: 2rem;
    }

    .metric-card {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.9));
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 1.5rem;
        border: 2px solid transparent;
        background-clip: padding-box;
        position: relative;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow:
            0 4px 20px rgba(0, 0, 0, 0.3),
            0 0 0 1px rgba(255, 255, 255, 0.05);
        overflow: hidden;
    }

    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        padding: 2px;
        background: linear-gradient(135deg, #8b5cf6, #ec4899, #06b6d4, #8b5cf6);
        border-radius: 20px;
        mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        mask-composite: exclude;
        -webkit-mask-composite: xor;
        opacity: 0;
        transition: opacity 0.3s ease;
    }

    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow:
            0 12px 40px rgba(0, 0, 0, 0.4),
            0 0 0 1px rgba(255, 255, 255, 0.1);
    }

    .metric-card:hover::before {
        opacity: 1;
    }

    .metric-content {
        display: flex;
        align-items: center;
        gap: 1rem;
        position: relative;
        z-index: 1;
    }

    .metric-icon {
        width: 48px;
        height: 48px;
        border-radius: 12px;
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(236, 72, 153, 0.2));
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        flex-shrink: 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .metric-text {
        flex: 1;
        min-width: 0;
    }

    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #ffffff 0%, #e0e7ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.25rem;
        line-height: 1;
        letter-spacing: -0.02em;
    }

    .metric-label {
        font-size: 0.875rem;
        color: #94a3b8;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.125rem;
    }

    .metric-subtitle {
        font-size: 0.75rem;
        color: #64748b;
        font-weight: 400;
        opacity: 0.8;
    }

    /* Section Cards */
    .section-card {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.8), rgba(30, 41, 59, 0.6));
        backdrop-filter: blur(20px);
        padding: 2rem;
        border-radius: 24px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
        margin-bottom: 2rem;
        transition: all 0.3s ease;
    }

    /* Heatmap card with green glow */
    .heatmap-card {
        border: 2px solid #22c55e;
        box-shadow: 0 0 20px rgba(34, 197, 94, 0.7),
                    0 20px 40px rgba(0, 0, 0, 0.3);
        animation: pulse-green 2s infinite;
    }

    @keyframes pulse-green {
        0%, 100% { box-shadow: 0 0 20px rgba(34, 197, 94, 0.7), 0 20px 40px rgba(0,0,0,0.3); }
        50% { box-shadow: 0 0 40px rgba(34, 197, 94, 1), 0 20px 40px rgba(0,0,0,0.3); }
    }

    .section-card:hover {
        border-color: rgba(255, 255, 255, 0.15);
        box-shadow: 0 32px 64px rgba(0, 0, 0, 0.4);
    }

    .section-title {
        font-size: 1.4rem;
        font-weight: 700;
        background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }

    .section-subtitle {
        font-size: 0.95rem;
        color: #cbd5e1;
        margin-bottom: 1rem;
        opacity: 0.8;
    }

    /* Step Cards */
    .step-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.6), rgba(51, 65, 85, 0.4));
        backdrop-filter: blur(15px);
        border-radius: 16px;
        padding: 1.25rem;
        border: 1px solid rgba(255, 255, 255, 0.06);
        margin-bottom: 1rem;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }

    .step-card::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 4px;
        background: linear-gradient(180deg, #8b5cf6 0%, #ec4899 100%);
        border-radius: 2px 0 0 2px;
    }

    .step-card:hover {
        transform: translateX(4px);
        border-color: rgba(255, 255, 255, 0.12);
        box-shadow: 0 12px 24px rgba(0, 0, 0, 0.3);
    }

    .step-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        color: #94a3b8;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }

    .step-service {
        font-size: 1.1rem;
        font-weight: 700;
        color: #f1f5f9;
        margin-bottom: 0.25rem;
    }

    .step-meta {
        font-size: 0.85rem;
        color: #cbd5e1;
        opacity: 0.8;
    }

    /* Chat Container */
    .chat-container {
        max-height: 600px;
        overflow-y: auto;
        padding: 1.5rem;
        border-radius: 20px;
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.7), rgba(30, 41, 59, 0.5));
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
    }

    /* Sidebar */
    .stSidebar {
        background: linear-gradient(180deg, #0f0c29 0%, #302b63 100%) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
        padding: 2rem 1rem;
    }

    .sidebar .sidebar-content {
        background: transparent !important;
    }

    /* Sidebar Navigation Buttons */
    .stSidebar .stButton button {
        display: flex !important;
        align-items: center;
        gap: 0.75rem;
        width: 100% !important;
        padding: 1rem 1.25rem !important;
        margin-bottom: 0.5rem !important;
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(236, 72, 153, 0.1)) !important;
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        color: #ffffff !important;
        text-decoration: none;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        cursor: pointer;
        position: relative;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        text-align: left !important;
        justify-content: flex-start !important;
    }

    .stSidebar .stButton button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
        transition: left 0.5s;
    }

    .stSidebar .stButton button:hover {
        transform: translateY(-3px) !important;
        border-color: rgba(255, 255, 255, 0.2) !important;
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.25), rgba(236, 72, 153, 0.25)) !important;
        box-shadow: 0 8px 24px rgba(139, 92, 246, 0.3) !important;
        text-shadow: 0 0 8px rgba(255, 255, 255, 0.5);
    }

    .stSidebar .stButton button:hover::before {
        left: 100%;
    }

    /* Regenerate Data Button - Special styling */
    .stSidebar .stButton button[data-testid="stBaseButton-primary"] {
        background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 50%, #06b6d4 100%) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 20px !important;
        padding: 1.5rem 1.25rem !important;
        margin-top: 2rem !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        box-shadow: 0 8px 24px rgba(139, 92, 246, 0.4) !important;
        text-shadow: 0 0 12px rgba(255, 255, 255, 0.8);
        justify-content: center !important;
    }

    .stSidebar .stButton button[data-testid="stBaseButton-primary"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        transition: left 0.6s;
    }

    .stSidebar .stButton button[data-testid="stBaseButton-primary"]:hover {
        transform: translateY(-4px) !important;
        box-shadow: 0 16px 40px rgba(139, 92, 246, 0.6) !important;
        background: linear-gradient(135deg, #7c3aed 0%, #db2777 50%, #0891b2 100%) !important;
        border-color: rgba(255, 255, 255, 0.4) !important;
    }

    .stSidebar .stButton button[data-testid="stBaseButton-primary"]:hover::before {
        left: 100%;
    }

    /* Upload Section */
    .upload-section {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.8), rgba(30, 41, 59, 0.6));
        backdrop-filter: blur(20px);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
    }

    .upload-section h3 {
        color: #e0e7ff;
        margin-bottom: 1rem;
        font-size: 1.1rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* Radio Buttons */
    .stRadio > div {
        gap: 0.5rem;
    }

    .stRadio label {
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(236, 72, 153, 0.1));
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 0.75rem 1rem;
        transition: all 0.3s ease;
        cursor: pointer;
        margin-bottom: 0.5rem;
    }

    .stRadio label:hover {
        border-color: rgba(255, 255, 255, 0.2);
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(236, 72, 153, 0.2));
        transform: translateY(-2px);
    }

    /* DataFrames */
    .stDataFrame {
        border-radius: 16px;
        overflow: hidden;
        background: rgba(15, 23, 42, 0.6);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.08);
    }

    /* Buttons */
    .stButton button {
        background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
    }

    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(139, 92, 246, 0.4);
        background: linear-gradient(135deg, #7c3aed 0%, #db2777 100%);
    }

    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }

    ::-webkit-scrollbar-track {
        background: rgba(15, 23, 42, 0.3);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #8b5cf6, #ec4899);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #7c3aed, #db2777);
    }

    /* AI Recommendation Card */
    .ai-recommendation-card {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.9));
        backdrop-filter: blur(20px);
        border-radius: 20px;
        border: 2px solid transparent;
        background-clip: padding-box;
        position: relative;
        overflow: hidden;
        box-shadow:
            0 8px 32px rgba(34, 197, 94, 0.3),
            0 0 0 1px rgba(34, 197, 94, 0.2);
    }

    .ai-recommendation-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        padding: 2px;
        background: linear-gradient(135deg, #22c55e, #16a34a, #15803d, #22c55e);
        border-radius: 20px;
        mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        mask-composite: exclude;
        -webkit-mask-composite: xor;
        opacity: 0.8;
        animation: glow 2s ease-in-out infinite alternate;
    }

    @keyframes glow {
        from {
            opacity: 0.6;
            box-shadow: 0 0 20px rgba(34, 197, 94, 0.4);
        }
        to {
            opacity: 1;
            box-shadow: 0 0 30px rgba(34, 197, 94, 0.8);
        }
    }

    .ai-recommendation-header {
        background: linear-gradient(135deg, rgba(34, 197, 94, 0.1), rgba(22, 163, 74, 0.1));
        padding: 1.5rem 1.5rem 1rem 1.5rem;
        font-size: 1.1rem;
        font-weight: 700;
        color: #ffffff;
        text-align: center;
        border-bottom: 1px solid rgba(34, 197, 94, 0.2);
        position: relative;
        z-index: 1;
    }

    .ai-recommendation-content {
        padding: 1.5rem;
        position: relative;
        z-index: 1;
    }

    .recommendation-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.75rem 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }

    .recommendation-item:last-child {
        border-bottom: none;
    }

    .item-label {
        font-size: 0.85rem;
        color: #94a3b8;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .item-value {
        font-size: 0.95rem;
        font-weight: 600;
        color: #ffffff;
        text-align: right;
    }

    .item-value.risk-low {
        color: #22c55e;
    }

    .item-value.risk-medium {
        color: #f97316;
    }

    .item-value.risk-high {
        color: #ef4444;
    }

    .item-value.improvement {
        color: #22c55e;
        font-weight: 700;
    }
</style>
    """,
    unsafe_allow_html=True,
)


def ensure_data():
    """Generate telemetry data if not exists."""
    data_path = os.path.join(PROJECT_ROOT, "data", "telemetry_data.csv")
    if not os.path.exists(data_path):
        df = generate_telemetry_data(num_days=14, records_per_edge=80)
        os.makedirs(os.path.dirname(data_path), exist_ok=True)
        df.to_csv(data_path, index=False)
        return df
    return pd.read_csv(data_path)


def get_telemetry_data():
    """Get telemetry data: use uploaded file if present, else default."""
    if "uploaded_telemetry" in st.session_state and st.session_state.uploaded_telemetry is not None:
        return st.session_state.uploaded_telemetry
    return ensure_data()


def generate_migration_batches(services, dependencies):
    """
    Determine migration batches using topological sorting.

    Nodes with no incoming dependencies can be migrated together in the same batch.
    Each batch consists of all services whose prerequisites have already been placed in
    earlier batches. The algorithm removes nodes layer-by-layer (Kahn's algorithm).

    Args:
        services: iterable of service names
        dependencies: list of (src, dst) tuples where src depends on dst

    Returns:
        List of batches, where each batch is a list of services.
    """
    import networkx as nx

    G = nx.DiGraph()
    G.add_nodes_from(services)
    G.add_edges_from(dependencies)

    batches = []
    # Kahn's algorithm
    working = G.copy()
    while working.nodes:
        # find nodes with no predecessors
        zero_indegree = [n for n, d in working.in_degree() if d == 0]
        if not zero_indegree:
            # cycle detected; put remaining nodes in their own batch
            batches.append(list(working.nodes()))
            break
        batches.append(zero_indegree)
        working.remove_nodes_from(zero_indegree)
    return batches


def create_dependency_graph(df):
    """
    Create an interactive PyVis network graph for service dependencies.

    Args:
        df: Telemetry DataFrame

    Returns:
        HTML string of the interactive network graph
    """
    # Get dependencies and risk scores
    deps = discover_dependencies(df=df)
    risk_df = calculate_risk_scores(df=df)

    # Create NetworkX graph
    G = build_dependency_graph(dependencies=deps)

    # Create PyVis network
    net = Network(height="600px", width="100%", bgcolor="#0f0c29", font_color="#ffffff")

    # Configure physics for better layout
    net.set_options("""
    {
      "physics": {
        "forceAtlas2Based": {
          "gravitationalConstant": -50,
          "centralGravity": 0.01,
          "springLength": 100,
          "springConstant": 0.08
        },
        "maxVelocity": 50,
        "solver": "forceAtlas2Based",
        "timestep": 0.35,
        "stabilization": {
          "enabled": true,
          "iterations": 1000
        }
      },
      "nodes": {
        "font": {
          "size": 14,
          "color": "#ffffff",
          "face": "Inter"
        },
        "borderWidth": 2,
        "shadow": true
      },
      "edges": {
        "color": {
          "color": "#8b5cf6",
          "opacity": 0.6
        },
        "width": 2,
        "shadow": true,
        "smooth": {
          "enabled": true,
          "type": "continuous"
        }
      },
      "interaction": {
        "hover": true,
        "multiselect": true,
        "navigationButtons": true
      }
    }
    """)

    # Add nodes with risk-based styling
    for node in G.nodes():
        # Get risk data for this service
        risk_data = risk_df[risk_df['service'] == node]
        if not risk_data.empty:
            risk_score = risk_data['risk_score'].iloc[0]
            risk_level = risk_data['risk_level'].iloc[0]
            dep_count = risk_data['dependency_count'].iloc[0]
        else:
            risk_score = 50  # Default medium risk
            risk_level = "Medium"
            dep_count = G.degree(node)

        # Set node size based on risk score (20-50 range)
        size = 20 + (risk_score / 100) * 30

        # Set node color based on risk level
        if risk_level == "High":
            color = "#ef4444"  # Red
        elif risk_level == "Medium":
            color = "#f97316"  # Orange
        else:  # Low
            color = "#22c55e"  # Green

        # Create hover title with details
        title = f"""
        <div style="background: rgba(15, 23, 42, 0.95); padding: 10px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);">
            <strong>{node}</strong><br>
            Risk Level: <span style="color: {color};">{risk_level}</span><br>
            Risk Score: {risk_score}<br>
            Dependencies: {dep_count}
        </div>
        """

        net.add_node(
            node,
            label=node,
            size=size,
            color=color,
            title=title,
            font={"size": 12, "color": "#ffffff"}
        )

    # Add edges
    for edge in G.edges():
        net.add_edge(edge[0], edge[1])

    # Generate HTML
    net.save_graph("temp_graph.html")

    # Read and return HTML content
    with open("temp_graph.html", "r", encoding="utf-8") as f:
        html_content = f.read()

    # Clean up temp file
    import os
    if os.path.exists("temp_graph.html"):
        os.remove("temp_graph.html")

    return html_content


def main():
    # Hero Section
    st.markdown('<p class="main-header">🚀 AI Cloud Migration Copilot</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Intelligent microservice migration planning with AI-powered insights and automated optimization</p>',
        unsafe_allow_html=True,
    )

    # Data source: upload or default
    telemetry_df = get_telemetry_data()

    # Pre-compute core analytics for KPIs and sections
    try:
        deps = discover_dependencies(df=telemetry_df)
    except Exception:
        deps = []

    try:
        risk_df = calculate_risk_scores(df=telemetry_df)
    except Exception:
        risk_df = pd.DataFrame()

    total_services = telemetry_df["service_name"].nunique() if "service_name" in telemetry_df.columns else len(
        telemetry_df
    )
    total_dependencies = len(deps)
    high_risk_services = (
        (risk_df["risk_level"] == "High").sum() if not risk_df.empty and "risk_level" in risk_df.columns else 0
    )
    avg_latency = (
        float(telemetry_df["request_latency"].mean())
        if "request_latency" in telemetry_df.columns
        else float(risk_df["avg_latency_ms"].mean()) if "avg_latency_ms" in risk_df.columns else 0.0
    )

    # Sidebar navigation + data upload
    with st.sidebar:
        # Upload Section
        st.markdown(
            """
            <div class="upload-section">
                <h3>📤 Upload Dataset</h3>
            </div>
            """,
            unsafe_allow_html=True,
        )

        upload_key = st.session_state.get("upload_key", 0)
        uploaded_file = st.file_uploader(
            "Upload CSV for testing",
            type=["csv"],
            help="Supports formats like cloud_migration_dataset_large.csv (service_name, depends_on, cpu_usage, etc.)",
            key=f"file_upload_{upload_key}",
        )
        if uploaded_file is not None:
            try:
                raw = pd.read_csv(uploaded_file)
                valid, msg = validate_uploaded_data(raw)
                if valid:
                    st.session_state.uploaded_telemetry = normalize_external_csv(raw)
                    st.success(f"Loaded {len(st.session_state.uploaded_telemetry)} rows")
                else:
                    st.error(msg)
            except Exception as e:
                st.error(f"Upload failed: {e}")
        if st.button("🔄 Use Default Data"):
            for key in ["uploaded_telemetry"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state.upload_key = st.session_state.get("upload_key", 0) + 1
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        # Navigation Buttons
        nav_options = [
            ("� Upload Dataset", "upload"),
            ("📊 Telemetry Viewer", "telemetry"),
            ("🕸️ Dependency Graph", "graph"),
            ("⚠️ Risk Analysis", "risk"),
            ("📋 Migration Plan", "plan"),
            ("🎯 Simulation", "simulation"),
            ("🤖 AI Assistant", "ai"),
            (" Download Report", "download"),
        ]

        # Initialize session state for navigation
        if "current_section" not in st.session_state:
            st.session_state.current_section = "telemetry"

        # Create navigation buttons
        for label, key in nav_options:
            icon = label.split()[0]
            text = " ".join(label.split()[1:])
            is_active = st.session_state.current_section == key

            button_class = "sidebar-nav-btn active" if is_active else "sidebar-nav-btn"

            if st.button(
                f"{icon} {text}",
                key=f"nav_{key}",
                help=f"Navigate to {text}",
                width='stretch',
            ):
                st.session_state.current_section = key
                st.rerun()

        # Regenerate Data Button
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("🔄 Regenerate Synthetic Data", key="regenerate_data", width='stretch', type="primary"):
            df = generate_telemetry_data(num_days=14, records_per_edge=80)
            df.to_csv(os.path.join(PROJECT_ROOT, "data", "telemetry_data.csv"), index=False)
            for key in ["uploaded_telemetry"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state.upload_key = st.session_state.get("upload_key", 0) + 1
            st.success("Data regenerated!")
            st.rerun()

    # Get current section
    section_map = {
        "upload": "� Upload Dataset",
        "telemetry": "📊 Telemetry Viewer",
        "graph": "🕸️ Dependency Graph",
        "risk": "⚠️ Risk Analysis",
        "plan": "📋 Migration Plan",
        "simulation": "🎯 Simulation",
        "ai": "🤖 AI Assistant",
        "download": "📥 Download Report",
    }
    section = section_map.get(st.session_state.current_section, "📊 Telemetry Viewer")

    # Global KPI overview (Section 1)
    st.markdown('<div class="kpi-row">', unsafe_allow_html=True)
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4, gap="large")

    with kpi_col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-content">
                    <div class="metric-icon">🏗️</div>
                    <div class="metric-text">
                        <div class="metric-label">Total Services</div>
                        <div class="metric-value">{total_services}</div>
                        <div class="metric-subtitle">Microservices discovered</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with kpi_col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-content">
                    <div class="metric-icon">🔗</div>
                    <div class="metric-text">
                        <div class="metric-label">Total Dependencies</div>
                        <div class="metric-value">{total_dependencies}</div>
                        <div class="metric-subtitle">Service interconnections</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with kpi_col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-content">
                    <div class="metric-icon">⚠️</div>
                    <div class="metric-text">
                        <div class="metric-label">High Risk Services</div>
                        <div class="metric-value">{high_risk_services}</div>
                        <div class="metric-subtitle">Require immediate attention</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with kpi_col4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-content">
                    <div class="metric-icon">⚡</div>
                    <div class="metric-text">
                        <div class="metric-label">Average Latency</div>
                        <div class="metric-value">{avg_latency:.1f}ms</div>
                        <div class="metric-subtitle">Performance metric</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)

    # Section: Upload Dataset (explicit)
    if section == "📂 Upload Dataset":
        with st.container():
            st.markdown(
                '<div class="section-card"><div class="section-title">📂 Dataset Upload</div>'
                '<div class="section-subtitle">Use the sidebar to upload a CSV and override the synthetic telemetry. '
                "Supported formats include your `cloud_migration_dataset_large.csv` file.</div></div>",
                unsafe_allow_html=True,
            )

    # Section 2: Telemetry Dataset Viewer / Dataset overview
    elif section == "📊 Telemetry Viewer":
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📊 Dataset Overview</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-subtitle">Preview the loaded telemetry and basic statistics.</div>',
            unsafe_allow_html=True,
        )

        with st.expander("Dataset preview & statistics", expanded=True):
            st.dataframe(telemetry_df.head(150), width='stretch')
            st.caption(f"Showing up to 150 of {len(telemetry_df)} rows")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Row Count", len(telemetry_df))
            with col2:
                st.metric("Unique Services", total_services)
            with col3:
                if "timestamp" in telemetry_df.columns:
                    st.metric(
                        "Time Range",
                        f"{str(telemetry_df['timestamp'].min())[:10]} → {str(telemetry_df['timestamp'].max())[:10]}",
                    )
                else:
                    st.metric(
                        "Data Source",
                        "Uploaded dataset" if "uploaded_telemetry" in st.session_state else "Synthetic telemetry",
                    )
        st.markdown("</div>", unsafe_allow_html=True)

    # Section 3: Service Dependency Graph
    elif section == "🕸️ Dependency Graph":
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-title">🕸️ Service Dependency Graph</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="section-subtitle">Interactive topology of microservice dependencies with AI-powered migration recommendations.</div>',
            unsafe_allow_html=True,
        )

        # Create two-column layout
        col1, col2 = st.columns([3, 1], gap="large")

        with col1:
            # Create and display PyVis network graph
            graph_html = create_dependency_graph(telemetry_df)
            components.html(graph_html, height=650, width=None)

        with col2:
            # AI Migration Recommendation Panel
            st.markdown(
                """
                <div class="ai-recommendation-card">
                    <div class="ai-recommendation-header">
                        🤖 AI Migration Recommendation
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Get AI recommendation
            risk_df = calculate_risk_scores(df=telemetry_df)
            recommendation = get_recommended_plan(compare_strategies(risk_df))

            # Calculate improvements (compared to worst strategy)
            all_strategies = compare_strategies(risk_df)
            worst_downtime = max(s["downtime_pct"] for s in all_strategies)
            worst_risk_score = max(s["avg_risk_score"] for s in all_strategies)

            downtime_reduction = ((worst_downtime - recommendation["downtime_pct"]) / worst_downtime * 100) if worst_downtime > 0 else 0
            risk_reduction = ((worst_risk_score - recommendation["avg_risk_score"]) / worst_risk_score * 100) if worst_risk_score > 0 else 0

            # Display recommendation details
            st.markdown(
                f"""
                <div class="ai-recommendation-content">
                    <div class="recommendation-item">
                        <span class="item-label">Best Strategy:</span>
                        <span class="item-value">{recommendation["strategy"].split(": ")[1]}</span>
                    </div>
                    <div class="recommendation-item">
                        <span class="item-label">Batch Size:</span>
                        <span class="item-value">{recommendation["batch_size"]}</span>
                    </div>
                    <div class="recommendation-item">
                        <span class="item-label">Risk Score:</span>
                        <span class="item-value risk-{recommendation["risk_level"].lower()}">{recommendation["risk_level"]}</span>
                    </div>
                    <div class="recommendation-item">
                        <span class="item-label">Est. Downtime Reduction:</span>
                        <span class="item-value improvement">+{downtime_reduction:.0f}%</span>
                    </div>
                    <div class="recommendation-item">
                        <span class="item-label">Risk Reduction:</span>
                        <span class="item-value improvement">+{risk_reduction:.0f}%</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Display metrics below the graph
        G = build_dependency_graph(dependencies=deps)
        metrics = get_graph_metrics(G)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Services (Nodes)", metrics["num_nodes"])
        with col2:
            st.metric("Dependencies (Edges)", metrics["num_edges"])
        with col3:
            st.metric("Entry Points", len(metrics["entry_points"]))

        st.markdown("</div>", unsafe_allow_html=True)

    # Section 4: Risk Analysis Dashboard
    elif section == "⚠️ Risk Analysis":
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-title">⚠️ Risk Analysis Dashboard</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="section-subtitle">Risk scores and resource pressure across services.</div>',
            unsafe_allow_html=True,
        )

        if risk_df.empty:
            st.warning("Risk scores could not be computed for the current dataset.")
        else:
            st.dataframe(risk_df, width='stretch', height=380)

            # Service Risk Heatmap
            if not risk_df.empty:
                fig_heat = px.scatter(
                    risk_df,
                    x="avg_latency_ms" if "avg_latency_ms" in risk_df.columns else "request_latency",
                    y="error_rate",
                    size="risk_score",
                    color="risk_level",
                    hover_name="service",
                    template="plotly_dark",
                    color_discrete_map={"Low": "#22c55e", "Medium": "#f97316", "High": "#ef4444"},
                    size_max=60,
                )
                fig_heat.update_layout(
                    title="Service Risk Heatmap",
                    xaxis_title="Latency (ms)",
                    yaxis_title="Error Rate",
                    margin=dict(l=40, r=40, t=40, b=40),
                    legend_title="Risk Level",
                )
                st.markdown('<div class="section-card heatmap-card">', unsafe_allow_html=True)
                st.plotly_chart(fig_heat, width='stretch')
                st.markdown('</div>', unsafe_allow_html=True)


            # CPU and error charts
            cpu_col, err_col = st.columns(2)
            with cpu_col:
                st.subheader("CPU Usage per Service")
                fig_cpu = px.bar(
                    risk_df,
                    x="service",
                    y="cpu_usage_pct",
                    color="risk_level",
                    color_discrete_sequence=px.colors.sequential.Blues_r,
                )
                fig_cpu.update_layout(
                    xaxis_title="Service",
                    yaxis_title="CPU Utilization (%)",
                    margin=dict(l=10, r=10, t=30, b=40),
                )
                st.plotly_chart(fig_cpu, width='stretch')
            with err_col:
                st.subheader("Error Rate per Service")
                fig_err = px.bar(
                    risk_df,
                    x="service",
                    y="error_rate",
                    color="risk_level",
                    color_discrete_sequence=px.colors.sequential.Reds,
                )
                fig_err.update_layout(
                    xaxis_title="Service",
                    yaxis_title="Error Rate",
                    margin=dict(l=10, r=10, t=30, b=40),
                )
                st.plotly_chart(fig_err, width='stretch')

            # Latency vs volume scatter
            st.subheader("Latency vs Request Volume")
            fig_scatter = px.scatter(
                risk_df,
                x="avg_latency_ms",
                y="request_volume",
                color="risk_level",
                hover_name="service",
                size="dependency_count",
                labels={"avg_latency_ms": "Average Latency (ms)", "request_volume": "Request Volume"},
                color_discrete_sequence=px.colors.sequential.Viridis,
            )
            fig_scatter.update_layout(margin=dict(l=10, r=10, t=30, b=40))
            st.plotly_chart(fig_scatter, width='stretch')

        st.markdown("</div>", unsafe_allow_html=True)

    # Section 5: Migration Plan
    elif section == "📋 Migration Plan":
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-title">📋 Migration Plan</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="section-subtitle">AI-recommended migration order, optimized for dependencies and risk.</div>',
            unsafe_allow_html=True,
        )

        plan = get_migration_order(risk_df=risk_df)

        # Get risk levels for display
        risk_level_map = dict(zip(risk_df["service"], risk_df["risk_level"]))

        # Visual step cards in responsive grid
        cols = st.columns(4)
        for step in plan:
            col = cols[(step["step"] - 1) % 4]
            risk_level = risk_level_map.get(step['service'], 'Medium')
            with col:
                st.markdown(
                    f"""
                    <div class="step-card">
                      <div class="step-label">STEP {step['step']}</div>
                      <div class="step-service">{step['service']}</div>
                      <div class="step-meta">Risk: {risk_level}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.subheader("Plan Details")
        st.dataframe(pd.DataFrame(plan), width='stretch', height=360)

        st.markdown("</div>", unsafe_allow_html=True)

    # Section 6: Migration Simulation
    elif section == "🎯 Simulation":
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-title">🎯 Migration Simulation</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="section-subtitle">Compare simulated migration strategies by downtime and aggregate risk.</div>',
            unsafe_allow_html=True,
        )

        sims = compare_strategies(risk_df=risk_df)
        recommended = get_recommended_plan(sims)

        st.success(
            f"Recommended: **{recommended['strategy']}** — "
            f"Downtime: **{recommended['downtime_pct']}%**, Risk: **{recommended['risk_level']}**"
        )

        # Strategy comparison visualization
        comp_df = pd.DataFrame([{
            "Strategy": s["strategy"],
            "Downtime %": s["downtime_pct"],
            "Risk Level": s["risk_level"],
            "Avg Risk Score": s["avg_risk_score"],
        } for s in sims])

        fig_sim = go.Figure()
        fig_sim.add_trace(
            go.Bar(
                x=comp_df["Strategy"],
                y=comp_df["Downtime %"],
                name="Downtime %",
                marker_color="#38bdf8",
            )
        )
        fig_sim.add_trace(
            go.Scatter(
                x=comp_df["Strategy"],
                y=comp_df["Avg Risk Score"],
                name="Avg Risk Score",
                mode="lines+markers",
                yaxis="y2",
                marker=dict(color="#f97316"),
            )
        )
        fig_sim.update_layout(
            yaxis=dict(title="Downtime (%)"),
            yaxis2=dict(title="Avg Risk Score", overlaying="y", side="right"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=10, r=10, t=30, b=40),
        )
        st.plotly_chart(fig_sim, width='stretch')

        st.subheader("Simulation Table")
        st.dataframe(comp_df, width='stretch', height=320)
        st.markdown("</div>", unsafe_allow_html=True)

    # Section 7: AI Assistant Chat
    elif section == "🤖 AI Assistant":
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-title">🤖 AI Migration Assistant</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="section-subtitle">Ask natural language questions about migration order, risk, and strategies.</div>',
            unsafe_allow_html=True,
        )

        if "messages" not in st.session_state:
            st.session_state.messages = []

        with st.container():
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        if prompt := st.chat_input("Ask about migration..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            response = answer_question(prompt)
            st.session_state.messages.append({"role": "assistant", "content": response})
            with st.chat_message("assistant"):
                st.markdown(response)

        st.markdown("</div>", unsafe_allow_html=True)

    # Section 8: Download Report (bonus)
    elif section == "📥 Download Report":
        st.header("8. Download Migration Report")
        try:
            risk_df = calculate_risk_scores(df=telemetry_df)
            plan = get_migration_order(risk_df=risk_df)
            cost_df = estimate_cloud_cost(df=telemetry_df)
            sims = compare_strategies(risk_df=risk_df)
            rec = get_recommended_plan(sims)
            try:
                failure_df = get_failure_predictions(df=telemetry_df)
            except Exception:
                failure_df = risk_df[["service"]].copy()
                failure_df["failure_probability"] = (risk_df["risk_score"] / 100).round(4)
                failure_df["predicted_risk"] = ["High" if r > 0.6 else "Low" for r in failure_df["failure_probability"]]
        except Exception as e:
            import traceback
            st.error(f"Error preparing report: {e}")
            st.code(traceback.format_exc(), language="text")
            st.stop()

        report = f"""
# AI Cloud Migration Copilot - Migration Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Executive Summary
- Total Services: {len(risk_df)}
- Recommended Strategy: {rec['strategy']}
- Estimated Downtime: {rec['downtime_pct']}%
- Total Monthly Cloud Cost: ${get_total_estimated_cost(cost_df):.2f}

## Migration Order
{format_migration_plan(plan)}

## Risk Analysis (Top 10)
{risk_df.head(10).to_string()}

## Cost Estimation
{cost_df.to_string()}

## Failure Predictions
{failure_df.to_string()}
"""
        st.download_button(
            "📥 Download Report (Markdown)",
            report,
            file_name=f"migration_report_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
            mime="text/markdown",
        )
        st.code(report[:2000] + "\n...", language="markdown")


if __name__ == "__main__":
    main()
