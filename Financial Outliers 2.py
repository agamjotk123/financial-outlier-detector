import streamlit as st
import pandas as pd
import numpy as np
import io

# 1. Page Configuration
st.set_page_config(page_title="Universal Outlier Detector", layout="wide")
st.title("📊 Universal KPI Outlier Detector")
st.write("Upload any Excel file, select your target columns, and automatically detect performance anomalies.")

# 2. File Upload
uploaded_file = st.file_uploader("Upload Excel File (.xlsx or .xlsb)", type=["xlsx", "xlsb"])

if uploaded_file is not None:
    try:
        file_ext = uploaded_file.name.split(".")[-1].lower()
        engine = "pyxlsb" if file_ext == "xlsb" else None
        
        df = pd.read_excel(uploaded_file, engine=engine)
        df.columns = df.columns.astype(str).str.strip()
        
        st.success("File uploaded successfully!")
        
        with st.expander("👀 Preview Raw Data", expanded=False):
            st.dataframe(df.head(10))

        # 3. Dynamic Column Selection
        st.subheader("⚙️ Configure Scan Parameters")
        all_columns = df.columns.tolist()
        
        col1, col2 = st.columns(2)
        with col1:
            entity_col = st.selectbox(
                "Select Entity / Category Column (e.g., Department, Region):", 
                options=all_columns
            )
        
        with col2:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            selected_kpis = st.multiselect(
                "Select Numerical KPI Columns to Scan:", 
                options=all_columns,
                default=numeric_cols[:3] if numeric_cols else []
            )

        sensitivity = st.slider("Outlier Sensitivity (Standard Deviations):", min_value=1.5, max_value=3.0, value=2.0, step=0.1)

        # 4. Outlier Detection Logic
        if st.button("🚀 Detect Outliers", type="primary"):
            if not selected_kpis:
                st.warning("Please select at least one numerical column to scan.")
            else:
                st.subheader("🚩 Analysis Results")
                
                all_outliers_df = pd.DataFrame()
                total_anomalies = 0
                
                for kpi in selected_kpis:
                    series = pd.to_numeric(df[kpi], errors='coerce')
                    mean = series.mean()
                    std = series.std()
                    
                    if std == 0 or pd.isna(std):
                        continue
                    
                    z_scores = (series - mean) / std
                    outlier_mask = z_scores.abs() > sensitivity
                    outlier_rows = df[outlier_mask].copy()
                    
                    if not outlier_rows.empty:
                        outlier_rows["Flagged_KPI"] = kpi
                        outlier_rows["KPI_Mean"] = round(mean, 2)
                        outlier_rows["Z_Score"] = round(z_scores[outlier_mask], 2)
                        all_outliers_df = pd.concat([all_outliers_df, outlier_rows], ignore_index=True)
                        total_anomalies += len(outlier_rows)

                # Summary Dashboard Metrics
                m1, m2, m3 = st.columns(3)
                m1.metric("Total Rows Analyzed", len(df))
                m2.metric("KPI Columns Scanned", len(selected_kpis))
                m3.metric("Total Outliers Found", total_anomalies)

                st.divider()

                if total_anomalies > 0:
                    st.dataframe(all_outliers_df[[entity_col, "Flagged_KPI", "KPI_Mean", "Z_Score"]], use_container_width=True)
                    
                    # Generate Downloadable Excel File in Memory
                    buffer = io.BytesIO()
                    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                        all_outliers_df.to_excel(writer, index=False, sheet_name='Outliers_Report')
                    
                    st.download_button(
                        label="📥 Download Outliers Excel Report",
                        data=buffer.getvalue(),
                        file_name="Anomalies_Report.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    st.info("No significant outliers detected with current sensitivity settings.")

    except Exception as e:
        st.error(f"Error processing file: {e}")