import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import text
from db import get_engine, get_year

st.set_page_config(page_title="Geographic Concentration", layout="wide")
st.title("Geographic and Sectoral Risk Concentration")

st.markdown("""
**Business Question:** Where is our carbon risk concentrated geographically and sectorally?

Understanding concentration risk enables:
- Country-specific exposure limits
- Sector diversification strategies
- Stress testing against carbon pricing scenarios
""")

QUERY = """
SELECT 
    c.country_name,
    c.region,
    s.sector_name,
    SUM(em.emissions_quantity) AS total_emissions_co2e,
    COUNT(DISTINCT es.source_id) AS num_sources
FROM emission_measurement em
JOIN emission_source es ON em.source_id = es.source_id
JOIN country c ON es.iso3_country = c.iso3_country
JOIN sector s ON es.sector_id = s.sector_id
WHERE em.gas = 'co2e_20yr'
  AND EXTRACT(YEAR FROM em.start_time) = :year
GROUP BY c.country_name, c.region, s.sector_name
ORDER BY total_emissions_co2e DESC
LIMIT 30
"""

year = get_year()
st.sidebar.header("Filters")
year = st.sidebar.selectbox("Select Year", options=[2023, 2022, 2021], index=[2023, 2022, 2021].index(year))

try:
    engine = get_engine()
    df = pd.read_sql(text(QUERY), engine, params={"year": year})

    st.subheader(f"Emissions by Region & Country — Top 30 ({year})")
    fig = px.treemap(
        df,
        path=['region', 'country_name'],
        values='total_emissions_co2e',
        color='total_emissions_co2e',
        color_continuous_scale='Reds',
        title=f'Geographic Carbon Concentration ({year})',
        labels={'total_emissions_co2e': 'Emissions (tonnes CO2e)'},
        height=600
    )
    fig.update_traces(textinfo='label+percent root')
    st.plotly_chart(fig, use_container_width=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Countries", df['country_name'].nunique())
    with col2:
        st.metric("Total Sectors", df['sector_name'].nunique())
    with col3:
        st.metric("Total Sources", f"{df['num_sources'].sum():,.0f}")

except Exception as e:
    st.error(f"Database error: {e}")
