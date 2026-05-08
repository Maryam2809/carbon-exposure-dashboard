import streamlit as st

st.markdown("""
### Data Source & Citation

This dashboard uses power sector emissions data from Climate TRACE:

**Citation:**  
Freeman, J., Rouzbeh Kargar, A., Couture, H., Jeyaratnam, J., Lewis, J., Alvara, M., Koenig, H., 
Nakano, T., Davitt, A., Lewis, C., and McCormick, G. (2025). Power sector: Emissions from Electricity 
Generation. WattTime, USA Pixel Scientia Labs, USA and Global Energy Monitor, USA, Climate TRACE 
Emissions Inventory. https://climatetrace.org [Accessed March 2025]

Data made available under [Creative Commons Attribution 4.0 International License (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).

### Data Processing & Transformations

The source data has been:
- Normalized to Third Normal Form (3NF) for relational database implementation

**Key Transformations:**
- Monthly emissions data aggregated to annual totals
- Ownership chains resolved to ultimate parent entities
- Geographic and sectoral classifications standardized
- Data quality metrics (confidence levels) integrated for regulatory compliance assessment

### Purpose & Scope

**Strictly for Educational Purposes:** Created for database implementation coursework at University 
(March 2025). Demonstrates application of relational database design, ETL processes, and business 
intelligence dashboards to real-world climate finance scenarios.

**Scenario Context:** Investment bank portfolio carbon risk assessment and financed emissions reporting, 
aligned with PCAF Standard and TCFD recommendations.

### Limitations & Disclaimers

- Emissions data provided "as is" by Climate TRACE
- This dashboard is for educational demonstration purposes only and should not be used for actual 
investment or risk management decisions without proper validation


See [Climate TRACE Terms of Use](https://climatetrace.org/terms) for complete licensing details.
""")