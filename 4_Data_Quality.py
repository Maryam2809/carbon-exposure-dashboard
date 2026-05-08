import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from sqlalchemy import text
from db import get_engine, get_year

st.set_page_config(page_title="Data Quality", layout="wide")
st.title("Data Quality Assessment for Regulatory Compliance")

st.markdown("""
**Business Question:** What percentage of our emissions data meets regulatory confidence thresholds?

Critical for:
- SEC climate disclosure requirements
- TCFD reporting
- EU Taxonomy compliance
- Scope 3 financed emissions calculations
""")

QUERY = """
SELECT 
    conf.emissions_quantity_confidence AS confidence_level,
    COUNT(*) AS measurement_count,
    SUM(em.emissions_quantity) AS total_emissions_co2e,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage_of_measurements
FROM confidence conf
JOIN emission_measurement em ON conf.source_id = em.source_id 
    AND conf.gas = em.gas 
    AND conf.start_time = em.start_time
WHERE em.gas = 'co2e_20yr'
  AND EXTRACT(YEAR FROM em.start_time) = :year
GROUP BY conf.emissions_quantity_confidence
ORDER BY 
    CASE conf.emissions_quantity_confidence
        WHEN 'very high' THEN 1
        WHEN 'high' THEN 2
        WHEN 'medium' THEN 3
        WHEN 'low' THEN 4
        WHEN 'very low' THEN 5
    END
"""

year = get_year()
st.sidebar.header("Filters")
year = st.sidebar.selectbox("Select Year", options=[2023, 2022, 2021], index=[2023, 2022, 2021].index(year))

try:
    engine = get_engine()
    df = pd.read_sql(text(QUERY), engine, params={"year": year})

    st.subheader(f"Measurement Count & Emissions Volume by Confidence Level ({year})")

    confidence_order = ['very high', 'high', 'medium', 'low', 'very low']
    color_map = {
        'very high': '#1a7a2e',
        'high':      '#5cb85c',
        'medium':    '#f0ad4e',
        'low':       '#e57a2a',
        'very low':  '#d9534f',
    }

    df['confidence_level'] = pd.Categorical(
        df['confidence_level'], categories=confidence_order, ordered=True
    )
    df = df.sort_values('confidence_level')
    df['color'] = df['confidence_level'].map(color_map)

    fig = go.Figure()

    # Bar 1: measurement count (left y-axis)
    fig.add_trace(go.Bar(
        name='Measurement Count',
        x=df['confidence_level'],
        y=df['measurement_count'],
        marker_color=df['color'].tolist(),
        yaxis='y1',
        text=df['percentage_of_measurements'].apply(lambda x: f"{x:.1f}%"),
        textposition='outside',
    ))

    # Bar 2: total emissions (right y-axis, semi-transparent)
    fig.add_trace(go.Bar(
        name='Total Emissions (t CO2e)',
        x=df['confidence_level'],
        y=df['total_emissions_co2e'],
        marker_color=df['color'].tolist(),
        marker_opacity=0.4,
        yaxis='y2',
    ))

    high_quality = df[
        df['confidence_level'].isin(['very high', 'high'])
    ]['measurement_count'].sum()
    total = df['measurement_count'].sum()
    high_quality_pct = (high_quality / total * 100) if total > 0 else 0

    fig.update_layout(
        title=f'Data Quality Profile — Measurements vs Emissions Volume ({year})',
        xaxis=dict(title='Confidence Level'),
        yaxis=dict(title='Number of Measurements', side='left'),
        yaxis2=dict(title='Total Emissions (t CO2e)', overlaying='y', side='right', showgrid=False),
        barmode='group',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        height=500,
        plot_bgcolor='rgba(0,0,0,0)',
        annotations=[dict(
            x=0.5, y=1.12, xref='paper', yref='paper',
            text=f"{'✅' if high_quality_pct >= 70 else '⚠️'} {high_quality_pct:.1f}% of measurements are high/very high confidence "
                 f"({'meets' if high_quality_pct >= 70 else 'below'} 70% regulatory threshold)",
            showarrow=False, font=dict(size=13),
            bgcolor='#d4edda' if high_quality_pct >= 70 else '#fff3cd',
            bordercolor='#28a745' if high_quality_pct >= 70 else '#ffc107',
            borderwidth=1, borderpad=6,
        )]
    )
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Database error: {e}")
