import streamlit as st
import pandas as pd
import numpy as np
import io

# 1. Page & Branding Configuration
st.set_page_config(
    page_title="FinPulse | AI Financial Anomaly Detector",
    page_icon="⚡",
    layout="wide"
)

# Custom Styling
st.markdown("""
    <style>
    .stApp {
        background-color: #0E1117;
    }
    .metric-card {
        background-color: #1E222D;
        border: 1px solid #2A2E39;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# 2. Header Section with Brand Logo
col_logo, col_title = st.columns([1, 8])
with col_logo:
    st.markdown("# ⚡")
with col_title:
    st.title("FinPulse Analytics")
    st.caption("Automated Financial Outlier & Anomaly Detection Engine")

st.divider()

# 3. Sidebar for Instructions & Sample Data Quick-Load
with st.sidebar:
    st.header("⚡ FinPulse QuickStart")
    st.markdown("Automate performance audits and flag metric anomalies instantly.")
    
    st.subheader("Try with Sample Data")
    if st.button("Load Sample Financial Dataset", type="secondary"):
        st.session_state["use_sample"] = True

    st.divider()
    st.caption("Built with Python, Pandas & Streamlit")

# 4. File Upload & Data Processing
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

if df is not None:
    df.columns = df.columns.astype(str).str.strip()
    
    with st.expander("👀 Dataset Preview", expanded=False):
        st.dataframe(df, use_container_width=True)

    st.subheader("⚙️ Analysis Parameters")
    all_columns = df.columns.tolist()
    
    c1, c2, c3 = st.columns(3)
    with c1:
        entity_col = st.selectbox("Entity Category Column:", options=all_columns)
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
            m3.metric("Anomalies Flagged", len(all_outliers), delta_color="inverse")

            if all_outliers:
                outlier_df = pd.DataFrame(all_outliers)
                st.dataframe(outlier_df, use_container_width=True)
                
                # Excel Export
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
                