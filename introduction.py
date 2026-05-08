import streamlit as st

st.set_page_config(
    page_title="Carbon Exposure Dashboard",
    page_icon="",
    layout="wide"
)

st.title("Carbon Exposure Analytics Dashboard")
st.markdown("""
**Scenario:** Investment bank portfolio carbon risk assessment using Climate TRACE emissions data.

This dashboard supports data-driven decision-making for:
- **Portfolio carbon exposure** quantification
- **Sectoral and geographic** risk concentration analysis  
- **Data quality assessment** for regulatory disclosure requirements

---

### Pages

Use the **sidebar** to navigate between analyses:

| Page | Description |
|------|-------------|
| **Portfolio Exposure** | Top 10 companies by attributed CO2e emissions |
| **Geographic Concentration** | Treemap of emissions by region and country |
| **Top Emitters Map** | Global map of highest-emitting facilities |
| **Data Quality** | Confidence level analysis for regulatory compliance |
| **Data Source Attribution** | Data Source Attribution |
""")

st.sidebar.header("Filters")
year = st.sidebar.selectbox("Select Year", options=[2023, 2022, 2021], index=0)
st.session_state["year"] = year