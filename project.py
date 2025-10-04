import pandas as pd
import requests
import streamlit as st
from sqlalchemy import create_engine
import mysql.connector

st.set_page_config(page_title="Harvard Artifact Explorer", layout="wide")

@st.cache_resource
def get_engine():
    try:
        # The only change is here: "mysqlconnector" is now "pymysql"
        conn_string = (
            f"mysql+pymysql://{st.secrets.database.db_user}:{st.secrets.database.db_pass}"
            f"@{st.secrets.database.db_host}/{st.secrets.database.db_name}"
        )
        engine = create_engine(conn_string)
        return engine
    except Exception as e:
        st.error(f"Failed to connect to the database. Please check your credentials in secrets.toml. Error: {e}")
        return None

engine = get_engine()

def create_tables():
    if engine is None:
        return
    conn = engine.connect()
    try:
        conn.exec_driver_sql("""
        CREATE TABLE IF NOT EXISTS artifact_metadata (
          id INT PRIMARY KEY, title TEXT, culture TEXT, period TEXT, century TEXT, medium TEXT,
          dimensions TEXT, description TEXT, department TEXT, classification TEXT,
          accessionyear INT, accessionmethod TEXT
        );
        """)
        conn.exec_driver_sql("""
        CREATE TABLE IF NOT EXISTS artifact_media (
          objectid INT PRIMARY KEY, imagecount INT, mediacount INT, colorcount INT,
          rank_value INT, datebegin INT, dateend INT,
          CONSTRAINT fk1_id FOREIGN KEY (objectid) REFERENCES artifact_metadata(id)
        );
        """)
        conn.exec_driver_sql("""
        CREATE TABLE IF NOT EXISTS artifact_colors (
          objectid INT, color TEXT, spectrum TEXT, hue TEXT, percent REAL, css3 TEXT,
          CONSTRAINT fk2_id FOREIGN KEY (objectid) REFERENCES artifact_metadata(id)
        );
        """)
        conn.commit()
    finally:
        conn.close()

if engine:
    create_tables()

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

def bulk_insert_with_ignore(table_name, columns, records):
    if not records or engine is None:
        return
    df = pd.DataFrame(records, columns=columns)
    df.to_sql(name=f'temp_{table_name}', con=engine, if_exists='replace', index=False)
    with engine.connect() as conn:
        conn.exec_driver_sql(f"""
            INSERT IGNORE INTO {table_name} ({', '.join(columns)})
            SELECT * FROM temp_{table_name};
        """)
        conn.exec_driver_sql(f"DROP TABLE temp_{table_name};")
        conn.commit()

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
    if engine:
        try:
            query = "SELECT COUNT(*) FROM artifact_metadata WHERE classification = %s"
            df_count = pd.read_sql(query, engine, params=(chosen_class,))
            record_count = df_count.iloc[0, 0]
            if record_count > 0:
                st.success(f"✅ Database already contains {record_count} records for '{chosen_class}'.")
            else:
                st.info(f"ℹ️ No data found for '{chosen_class}' in the database.")
        except Exception as e:
            st.warning(f"Could not check database: {e}")

        if st.button(f"Fetch & Store {chosen_class} Data"):
            with st.spinner("Fetching data from Harvard API... ⏳"):
                records = fetch_classifications(chosen_class, pages=25)
            if records:
                meta, media, colors = artifact_details(records)
                with st.spinner("Inserting data into the database... 💾"):
                    bulk_insert_with_ignore('artifact_metadata', [
                        "id", "title", "culture", "period", "century", "medium", "dimensions",
                        "description", "department", "classification", "accessionyear", "accessionmethod"
                    ], meta)
                    bulk_insert_with_ignore('artifact_media', [
                        "objectid", "imagecount", "mediacount", "colorcount", "rank_value", "datebegin", "dateend"
                    ], media)
                    bulk_insert_with_ignore('artifact_colors', [
                        "objectid", "color", "spectrum", "hue", "percent", "css3"
                    ], colors)
                st.success(f"✅ Successfully inserted/updated data for {chosen_class}.")
                st.balloons()
            else:
                st.error("Failed to fetch data. Nothing was inserted.")

with tab2:
    st.header(f"Explore Database Tables for '{chosen_class}'")
    if engine:
        table_choice = st.selectbox("📂 Choose a Table", ["artifact_metadata", "artifact_media", "artifact_colors"])
        if st.button("📖 Show Table Data"):
            if table_choice == "artifact_metadata":
                query = "SELECT * FROM artifact_metadata WHERE classification = %s;"
            else:
                query = f"""
                    SELECT t.* FROM {table_choice} t
                    JOIN artifact_metadata m ON t.objectid = m.id
                    WHERE m.classification = %s;
                """
            try:
                df = pd.read_sql(query, engine, params=(chosen_class,))
                st.success(f"✅ Loaded {len(df)} rows from **{table_choice}** for '{chosen_class}'")
                st.dataframe(df)
            except Exception as e:
                st.error(f"Failed to execute query: {e}")

with tab3:
    st.header("📊 Query & Visualization Workspace")
    if engine:
        query_options = [
            "Select a query...",
            "1. List artifacts from a specific department",
            "2. Count artifacts per department",
            "3. Find artifacts with no description",
        ]
        selected_query = st.selectbox("✨ Select a Pre-built Query", query_options)

        query = ""
        params = None
        run_query = False

        if selected_query == query_options[1]:
            department_name = st.text_input("Enter Department Name", value="Drawings", key="q1_dept")
            if st.button("🚀 Run Query", key="run_q1"):
                query = "SELECT id, title FROM artifact_metadata WHERE department = %s;"
                params = (department_name,)
                run_query = True
        elif selected_query == query_options[2]:
            if st.button("🚀 Run Query", key="run_q2"):
                query = "SELECT department, COUNT(*) AS artifact_count FROM artifact_metadata GROUP BY department ORDER BY artifact_count DESC;"
                run_query = True
        elif selected_query == query_options[3]:
            if st.button("🚀 Run Query", key="run_q3"):
                query = "SELECT id, title FROM artifact_metadata WHERE description IS NULL OR description = '';"
                run_query = True

        if run_query and query:
            try:
                df_query = pd.read_sql(query, engine, params=params)
                st.success(f"✅ Query executed successfully! Rows returned: {len(df_query)}")
                st.dataframe(df_query)
            except Exception as e:
                st.error(f"Query failed: {e}")
