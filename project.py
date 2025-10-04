import pandas as pd
import requests
import streamlit as st
from sqlalchemy import create_engine
import mysql.connector

st.set_page_config(page_title="Harvard Artifact Explorer", layout="wide")

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

# engine = get_engine()

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

# THESE TWO LINES ARE NOW DISABLED FOR THE TEST
# if engine:
#    create_tables()

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
    artifact_metadata, artifact_media, artifact_colors = [], [], []
    for i in all_records:
        artifact_metadata.append((
            i.get('id'), i.get('title'), i.get('culture'), i.get('period'), i.get('century'),
            i.get('medium'), i.get('dimensions'), i.get('description'), i.get('department'),
            i.get('classification'), i.get('accessionyear'), i.get('accessionmethod')
        ))
        artifact_media.append((
            i.get('id'), i.get('imagecount'), i.get('mediacount'), i.get('colorcount'),
            i.get('rank'), i.get('datebegin'), i.get('dateend')
        ))
        colors = i.get('colors')
        if colors:
            for j in colors:
                artifact_colors.append((
                    i.get('id'), j.get('color'), j.get('spectrum'), j.get('hue'),
                    j.get('percent'), j.get('css3')
                ))
    return artifact_metadata, artifact_media, artifact_colors

def bulk_insert(table_name, columns, records):
    if not records or engine is None:
        return
    df = pd.DataFrame(records, columns=columns)
    df.to_sql(table_name, con=engine, if_exists='append', index=False)


st.markdown("""
    <div style='text-align:center; background:linear-gradient(to right, #ffffff, #fdf5e6);
                padding:20px; border-radius:15px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);'>
        <h1 style='color:#B22222; font-size:46px; font-family:Georgia;'>🏛 Harvard Artifact Explorer</h1>
        <p style='color:#333333; font-size:20px; font-family:Trebuchet MS;'>
            Discover the beauty of history with <b style='color:#DAA520;'>golden insights</b> into Harvard Art Museum artifacts.
        </p>
    </div>
""", unsafe_allow_html=True)
st.markdown("---")

st.sidebar.markdown("""
    <div style='text-align:center; padding:15px; background:linear-gradient(to bottom, #fff, #fdf5e6);
                border-radius:12px; box-shadow: 0 3px 6px rgba(0,0,0,0.1);'>
        <h2 style='color:#B22222; font-family:Georgia;'>🔍 Controls</h2>
    </div>
""", unsafe_allow_html=True)
chosen_class = st.sidebar.selectbox("Choose a classification", ["Paintings", "Sculpture", "Drawings", "Fragments", "Photographs"])

tab1, tab2, tab3 = st.tabs(["📥 Data Loader", "🗃️ Database Explorer", "✍️ SQL Workspace"])

with tab1:
    st.header(f"Load Data for: {chosen_class}")
    st.info("Database connection is currently disabled for testing.") # Added an info box

with tab2:
    st.header(f"Explore Database Tables for '{chosen_class}'")
    st.info("Database connection is currently disabled for testing.")

with tab3:
    st.header("📊 Query & Visualization Workspace")
    st.info("Database connection is currently disabled for testing.")
