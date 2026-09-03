import streamlit as st
import pandas as pd
import numpy as np
import io

# 1. Page & App Branding Configuration
st.set_page_config(
    page_title="FinPulse | AI Outlier Detector",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. PWA Meta Tags & High-End Light Blue / Black Custom CSS
st.markdown("""
    <head>
        <link rel="manifest" href="manifest.json">
        <meta name="theme-color" content="#0B0F19">
        <meta name="mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
        <meta name="apple-mobile-web-app-title" content="FinPulse">
    </head>
    
    <style>
    /* Dark Electric Blue Gradient Background */
    .stApp {
        background: linear-gradient(135deg, #060911 0%, #0B132B 50%, #1C2541 100%);
        color: #F0F4F8;
    }
    
    /* Header Styling */
    .brand-title {
        font-size: 2.6rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38BDF8 0%, #818CF8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    
    .brand-sub {
        color: #94A3B8;
        font-size: 1.05rem;
        margin-bottom: 20px;
    }
    
    /* Custom Blue Glassmorphism Container Cards */
    div[data-testid="stMetric"], div.stDataFrame, .css-1r6slb0 {
        background: rgba(15, 23, 42, 0.75) !important;
        border: 1px solid rgba(56, 189, 248, 0.25) !important;
        border-radius: 12px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        padding: 15px !important;
    }
    
    /* Metric Value Styling */
    div[data-testid="stMetricValue"] {
        color: #38BDF8 !important;
        font-weight: 700 !important;
    }

    /* Primary Electric Blue Button */
    .stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #0284C7 0%, #2563EB 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.6rem 1.2rem !important;
        box-shadow: 0 4px 14px 0 rgba(14, 165, 233, 0.39) !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0B0F19 !important;
        border-right: 1px solid rgba(56, 189, 248, 0.15) !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Header Section
st.markdown('<p class="brand-title">⚡ FinPulse Analytics</p>', unsafe_allow_html=True)
st.markdown('<p class="brand-sub">Autonomous Financial Outlier & Anomaly Detection Platform</p>', unsafe_allow_html=True)

# 4. Sidebar Options & QuickStart
with st.sidebar:
    st.markdown("<h3 style='color: #38BDF8;'>⚡ Quick Controls</h3>", unsafe_allow_html=True)
    st.write("Upload operational workbooks or load the demo environment.")
    
    if st.button("🔄 Load Demo Financial Data", type="secondary"):
        st.session_state["use_sample"] = True

    st.divider()
    st.markdown("<p style='color: #64748B; font-size: 0.85rem;'>Version 2.0 • Light-Blue Theme</p>", unsafe_allow_html=True)

# 5. Data Handler
uploaded_file = st.file_uploader("Upload Excel File (.xlsx or .xlsb)", type=["xlsx", "xlsb"])
df = None

if uploaded_file is not None:
    try:
        file_ext = uploaded_file.name.split(".")[-1].lower()
        engine = "pyxlsb" if file_ext == "xlsb" else None
        df = pd.read_excel(uploaded_file, engine=engine)
    except Exception as e:
        st.error(f"Error loading file: {e}")

elif st.session_state.get("use_sample", False):
    sample_data = {
        "Department": ["Marketing", "Sales", "Engineering", "Operations", "HR", "Finance", "Product", "IT"],
        "Monthly_Budget_USD": [45000, 120000, 350000, 85000, 40000, 50000, 210000, 95000],
        "Actual_Spend_USD": [48000, 115000, 890000, 82000, 41000, 51000, 215000, 98000],
        "Variance_Pct": [0.06, -0.04, 1.54, -0.03, 0.02, 0.02, 0.02, 0.03]
    }
    df = pd.DataFrame(sample_data)
    st.info("Loaded pre-configured financial sample dataset!")

# 6. Analysis Section
if df is not None:
    df.columns = df.columns.astype(str).str.strip()
    
    with st.expander("🔍 Dataset Preview", expanded=False):
        st.dataframe(df, use_container_width=True)

    st.subheader("⚙️ Scan Parameters")
    all_columns = df.columns.tolist()
    
    c1, c2, c3 = st.columns(3)
    with c1:
        entity_col = st.selectbox("Entity / Category Column:", options=all_columns)
    with c2:
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        selected_kpis = st.multiselect("Target KPI Columns:", options=all_columns, default=numeric_cols[:2] if numeric_cols else [])
    with c3:
        sensitivity = st.slider("Z-Score Sensitivity Threshold:", min_value=1.0, max_value=3.0, value=1.5, step=0.1)

    if st.button("🚀 Run Anomaly Scan", type="primary"):
        if not selected_kpis:
            st.warning("Please select at least one numeric column to analyze.")
        else:
            all_outliers = []
            
            for kpi in selected_kpis:
                series = pd.to_numeric(df[kpi], errors='coerce')
                mean = series.mean()
                std = series.std()
                
                if std > 0:
                    z_scores = (series - mean) / std
                    outliers = df[z_scores.abs() > sensitivity].copy()
                    for idx, row in outliers.iterrows():
                        all_outliers.append({
                            "Entity": row[entity_col],
                            "KPI Metric": kpi,
                            "Flagged Value": row[kpi],
                            "Category Mean": round(mean, 2),
                            "Z-Score Severity": round(z_scores[idx], 2)
                        })

            st.divider()
            st.subheader("📊 Audit Dashboard")
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Rows Processed", len(df))
            m2.metric("KPIs Scanned", len(selected_kpis))
            m3.metric("Anomalies Flagged", len(all_outliers))

            if all_outliers:
                outlier_df = pd.DataFrame(all_outliers)
                st.dataframe(outlier_df, use_container_width=True)
                
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    outlier_df.to_excel(writer, index=False, sheet_name='Audit_Summary')
                
                st.download_button(
                    label="📥 Download Audit Report (.xlsx)",
                    data=buffer.getvalue(),
                    file_name="FinPulse_Anomaly_Report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.success("No anomalies detected based on the configured sensitivity.")