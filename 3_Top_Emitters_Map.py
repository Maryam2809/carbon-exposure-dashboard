import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import text
from db import get_engine, get_year

st.set_page_config(page_title="Top Emitters Map", layout="wide")
st.title("Geographic Distribution of Top Emitters")

st.markdown("""
**Business Question:** Where are the highest-emitting facilities physically located?

Enables:
- Physical climate risk assessment (flood, drought, extreme weather exposure)
- Geographic concentration analysis
- Jurisdiction-specific regulatory risk (carbon pricing, phase-out mandates)
""")

QUERY = """
SELECT 
    es.source_name,
    es.source_id,
    c.country_name,
    s.sector_name,
    es.lat,
    es.lon,
    SUM(em.emissions_quantity) AS annual_emissions_co2e
FROM emission_measurement em
JOIN emission_source es ON em.source_id = es.source_id
JOIN country c ON es.iso3_country = c.iso3_country
JOIN sector s ON es.sector_id = s.sector_id
WHERE em.gas = 'co2e_20yr'
  AND EXTRACT(YEAR FROM em.start_time) = :year
  AND es.lat IS NOT NULL
  AND es.lon IS NOT NULL
GROUP BY es.source_name, es.source_id, c.country_name, s.sector_name, es.lat, es.lon
ORDER BY annual_emissions_co2e DESC
LIMIT 10
"""

year = get_year()
st.sidebar.header("Filters")
year = st.sidebar.selectbox("Select Year", options=[2023, 2022, 2021], index=[2023, 2022, 2021].index(year))

try:
    engine = get_engine()
    df = pd.read_sql(text(QUERY), engine, params={"year": year})

    st.subheader(f"Top 10 Emitting Facilities — Global Map ({year})")
    fig = px.scatter_mapbox(
        df,
        lat='lat',
        lon='lon',
        size='annual_emissions_co2e',
        color='sector_name',
        hover_name='source_name',
        hover_data={
            'country_name': True,
            'sector_name': True,
            'annual_emissions_co2e': ':,.0f',
            'lat': False,
            'lon': False
        },
        labels={
            'annual_emissions_co2e': 'Annual Emissions (tonnes CO2e)',
            'sector_name': 'Sector',
            'country_name': 'Country'
        },
        zoom=1,
        height=600,
        mapbox_style="carto-positron"
    )
    fig.update_layout(
        title=f'Top 10 Highest-Emitting Facilities ({year})',
        margin={"r": 0, "t": 40, "l": 0, "b": 0}
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Facility Details")
    display = df[['source_name', 'country_name', 'sector_name', 'annual_emissions_co2e']].copy()
    display['annual_emissions_co2e'] = display['annual_emissions_co2e'].apply(lambda x: f"{x:,.0f}")
    st.dataframe(display, use_container_width=True)

except Exception as e:
    st.error(f"Database error: {e}")
