import streamlit as st
from sqlalchemy import create_engine


@st.cache_resource
def get_engine():
    db_url = st.secrets["database"]["url"]
    return create_engine(
        db_url,
        pool_pre_ping=True,
        connect_args={
            "connect_timeout": 10,
            "keepalives": 1,
            "keepalives_idle": 30,
            "keepalives_interval": 10,
            "keepalives_count": 5,
        },
    )


def get_year():
    """Return the year selected on the home page sidebar, default 2023."""
    return st.session_state.get("year", 2023)
