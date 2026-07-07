import os
import sqlite3
import pandas as pd
from pathlib import Path
import plotly.express as px
import requests
import streamlit as st
from dotenv import load_dotenv

# Loading environmental variables
load_dotenv()

st.set_page_config(
    page_title="Veritas Claims Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_PATH = "../../veritas_claims.db"
RAW_DIR = Path("../../sample-data/raw")
PROCESSED_DIR = Path("../../sample-data/processed")
DUPLICATES_DIR = Path("../../sample-data/duplicates")
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")


def fetch_analytics_summary() -> pd.DataFrame:
    try:
        with sqlite3.connect(DB_PATH) as conn:
            query = """
                SELECT test_analytics, COUNT(*) as count 
                FROM medical_records 
                GROUP BY test_analytics
            """
            return pd.read_sql_query(query, conn)
    except Exception:
        return pd.DataFrame(columns=["test_analytics", "count"])


def start_processing():
    try:
        response = requests.post(f"{BACKEND_URL}/api/v1/processing", timeout=60)
        if response.status_code == 200:
            st.sidebar.success("Ingestion engine completed processing successfully!")
            st.rerun()  
        else:
            st.sidebar.error(f"Backend Processing Failed. Status Code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        st.sidebar.error(f"Connection Error: Unable to reach API at {BACKEND_URL}. Details: {e}")
        

def clear_db():
    try:
        response = requests.get(f"{BACKEND_URL}/restart-db",timeout=60)
        
        if response.status_code == 200:
            st.sidebar.success("Database Cleared successfully .")
            st.rerun()  
        else:
            st.sidebar.error(f"Backend Processing Failed. Status Code: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        st.sidebar.error(f"Connection Error: Unable to reach API at {BACKEND_URL}. Details: {e}")

def fetch_recent_records() -> pd.DataFrame:
    try:
        with sqlite3.connect(DB_PATH) as conn:
            query = """
                SELECT trace_id, claim_no, patient_name, reports_date, processed_at
                FROM medical_records
                GROUP BY trace_id
                ORDER BY processed_at DESC
                LIMIT 10
            """
            return pd.read_sql_query(query, conn)
    except Exception:
        return pd.DataFrame()


def get_file_counts():
    raw = len(list(RAW_DIR.glob("*.json"))) if RAW_DIR.exists() else 0
    processed = len(list(PROCESSED_DIR.glob("*.json"))) if PROCESSED_DIR.exists() else 0
    failed = len(list(DUPLICATES_DIR.glob("*.json"))) if DUPLICATES_DIR.exists() else 0
    return raw, processed, failed


raw_count, processed_count, failed_count = get_file_counts()
analytics_df = fetch_analytics_summary()

outliers = analytics_df[analytics_df['test_analytics'] == 'Outlier']['count'].sum()
out_of_range = analytics_df[analytics_df['test_analytics'].isin(['Above Range', 'Below Range'])]['count'].sum()
total_files = processed_count + failed_count

with st.sidebar:
    st.header("Pipeline Management")
    st.markdown("Control ingestion flows and manage active directory jobs.")
    st.markdown("---")
    
    st.markdown("### Staging Health")
    if raw_count > 0:
        st.warning(f"Pending Input Queue: **{raw_count} file(s)**")
        if st.button("Run Ingestion Pipeline", type="primary", use_container_width=True):
            with st.spinner("Executing pipeline ingestion analytics..."):
                start_processing()
    else:
        st.success("Ingestion queue clear! No files pending.")
        st.button("Run Ingestion Pipeline", type="primary", disabled=True, use_container_width=True)
        
    st.markdown("---")
    if st.button("Clear DB",use_container_width=True):
        with st.spinner("Executing database cleaning mechanism..."):
            clear_db()
        
    if st.button("Refresh", use_container_width=True):
        st.rerun()
        
    


st.title("Veritas Claims Pipeline")
st.caption("Active Ingestion Metrics, Automated Diagnostic Range Boundary Auditing, & Loss Control Monitoring")
st.markdown("---")


col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="Total Batches of Files Received", value=total_files)
with col2:
    st.metric(label="Successfully Standardized", value=processed_count, delta=f"{processed_count} Transferred")
with col3:
    st.metric(label="DLQ Exceptions / Duplicates", value=failed_count, delta=f"-{failed_count} Isolated" if failed_count > 0 else "0 Violations", delta_color="inverse")
with col4:
    st.metric(label="Clinical Outliers Flagged", value=int(outliers), delta=f"{int(out_of_range)} out-of-bounds metrics")

st.markdown("---")

chart_col, table_col = st.columns([4, 5])

with chart_col:
    st.markdown("### Quality Control Breakdown")
    if not analytics_df.empty:
        fig = px.pie(
            analytics_df, 
            values='count', 
            names='test_analytics', 
            color='test_analytics',
            color_discrete_map={
                'Within Range': '#2ecc71',     
                'Above Range': '#f1c40f',       
                'Below Range': '#3498db',      
                'Outlier': '#e74c3c',          
                'Invalid/Non-Numeric': '#95a5a6' 
            },
            hole=0.45
        )
        
        fig.update_layout(margin=dict(t=20, b=20, l=10, r=10), legend=dict(orientation="h", y=-0.1))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Please provide medical records to analyse trends")


st.markdown("---")


st.markdown("### Pipeline Audit Logs (Last 10 Unique Records)")
recent_df = fetch_recent_records()

if not recent_df.empty:
    st.data_editor(
        recent_df, 
        column_config={
            "trace_id": st.column_config.TextColumn("Trace ID", width="large"),
            "claim_no": st.column_config.TextColumn("Claim Reference No", width="medium"),
            "patient_name": st.column_config.TextColumn("Patient Identifier", width="medium"),
            "reports_date": st.column_config.TextColumn("Clinical Specimen Date", width="medium"),
            "processed_at": st.column_config.TextColumn("Ingestion Handshake Time", width="large")
        },
        hide_index=True,
        use_container_width=True,
        disabled=True 
    )
else:
    st.info("System is initialised. Please provide valid data content")