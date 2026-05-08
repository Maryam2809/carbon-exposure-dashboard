import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import text
from db import get_engine, get_year

st.set_page_config(page_title="Portfolio Exposure", layout="wide")
st.title("Portfolio Carbon Exposure by Parent Company")

st.markdown("""
**Business Question:** Which corporate entities create the most carbon exposure for our portfolio?

This analysis calculates attributed emissions based on ownership stakes, enabling:
- Identification of highest-risk counterparties
- Portfolio rebalancing decisions
- Engagement prioritization for emissions reduction
""")

QUERY = """
SELECT 
    ce.entity_name AS parent_company,
    ce.entity_type,
    c.country_name,
    c.region,
    s.sector_name,
    s.subsector_name,
    COUNT(DISTINCT es.source_id) AS num_facilities,
    SUM(em.emissions_quantity * (COALESCE(o.overall_share_percent, 0) / 100)) AS attributed_emissions_co2e,
    AVG(o.overall_share_percent) AS avg_ownership_pct
FROM ownership o
JOIN corporate_entity ce ON o.ultimate_owner_id = ce.entity_id
JOIN emission_source es ON o.source_id = es.source_id
JOIN country c ON es.iso3_country = c.iso3_country
JOIN sector s ON es.sector_id = s.sector_id
JOIN emission_measurement em ON es.source_id = em.source_id
WHERE em.gas = 'co2e_20yr'
  AND EXTRACT(YEAR FROM em.start_time) = :year
GROUP BY ce.entity_name, ce.entity_type, c.country_name, c.region, 
         s.sector_name, s.subsector_name
ORDER BY attributed_emissions_co2e DESC
"""

year = get_year()
st.sidebar.header("Filters")
year = st.sidebar.selectbox("Select Year", options=[2023, 2022, 2021], index=[2023, 2022, 2021].index(year))

try:
    engine = get_engine()
    df = pd.read_sql(text(QUERY), engine, params={"year": year})

    st.subheader(f"Top 10 Carbon-Exposed Entities ({year})")
    top_10 = df.head(10)[
        ['parent_company', 'entity_type', 'sector_name',
         'num_facilities', 'attributed_emissions_co2e', 'avg_ownership_pct']
    ].copy()
    top_10['attributed_emissions_co2e'] = top_10['attributed_emissions_co2e'].apply(lambda x: f"{x:,.0f}")
    st.dataframe(top_10, use_container_width=True)

    st.subheader("Top 10 Attributed Emissions by Company")
    fig = px.bar(
        df.head(10),
        x='parent_company',
        y='attributed_emissions_co2e',
        color='sector_name',
        title=f'Top 10 Companies by Attributed CO2e Emissions ({year})',
        labels={
            'attributed_emissions_co2e': 'Attributed Emissions (tonnes CO2e)',
            'parent_company': 'Parent Company',
            'sector_name': 'Sector'
        },
        height=500
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Database error: {e}")
