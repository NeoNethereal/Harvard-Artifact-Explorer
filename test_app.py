import pandas as pd
import requests
import streamlit as st
from sqlalchemy import create_engine
import mysql.connector

# Copied from project.py
@st.cache_resource
def get_engine():
    try:
        conn_string = (
            f"mysql+mysqlconnector://{st.secrets.database.db_user}:{st.secrets.database.db_pass}"
            f"@{st.secrets.database.db_host}/{st.secrets.database.db_name}"
        )
        engine = create_engine(conn_string)
        return engine
    except Exception as e:
        st.error(f"Failed to connect to the database. Please check your credentials in secrets.toml. Error: {e}")
        return None

def create_tables():
    if engine is None:
        return
    conn = engine.connect()
    try:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS artifact_metadata (
          id INT PRIMARY KEY, title TEXT, culture TEXT, period TEXT, century TEXT, medium TEXT,
          dimensions TEXT, description TEXT, department TEXT, classification TEXT,
          accessionyear INT, accessionmethod TEXT
        );
        """)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS artifact_media (
          objectid INT PRIMARY KEY, imagecount INT, mediacount INT, colorcount INT,
          rank_value INT, datebegin INT, dateend INT,
          CONSTRAINT fk1_id FOREIGN KEY (objectid) REFERENCES artifact_metadata(id)
        );
        """)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS artifact_colors (
          objectid INT, color TEXT, spectrum TEXT, hue TEXT, percent REAL, css3 TEXT,
          CONSTRAINT fk2_id FOREIGN KEY (objectid) REFERENCES artifact_metadata(id)
        );
        """)
    finally:
        conn.close()

@st.cache_data
def fetch_classifications(classi, pages=25):
    all_records = []
    url = 'https://api.harvardartmuseums.org/object'
    for page in range(1, pages + 1):
        params = {
            'apikey': st.secrets.api.harvard_api_key,
            'size': 100,
            'page': page,
            'classification': classi
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            all_records.extend(data.get('records', []))
        except requests.exceptions.RequestException as e:
            st.error(f"API request failed: {e}")
            return []
    return all_records

def artifact_details(all_records):
    # ... (include the full function code here) ...
    return artifact_metadata, artifact_media, artifact_colors

def bulk_insert(table_name, columns, records):
    # ... (include the full function code here) ...
    pass


# Original UI Code
st.markdown("""
    <div style='text-align:center; background:linear-gradient(to right, #ffffff, #fdf5e6);
                padding:20px; border-radius:15px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);'>
        <h1 style='color:#B22222; font-size:46px; font-family:Georgia;'>🏛 Harvard Artifact Explorer</h1>
        <p style='color:#333333; font-size:20px; font-family:Trebuchet MS;'>
            Discover the beauty of history with <b style='color:#DAA520;'>golden insights</b> into Harvard Art Museum artifacts.
        </p>
    </div>
""", unsafe_allow_html=True)
