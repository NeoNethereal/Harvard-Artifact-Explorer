import pandas as pd
import requests
import streamlit as st
from sqlalchemy import create_engine

st.set_page_config(page_title="Harvard Artifact Explorer", layout="wide")

@st.cache_resource
def get_engine():
    try:
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
            "1.  List all artifacts from the 11th century belonging to Byzantine culture",
            "2.  What are the unique cultures represented in the artifacts?",
            "3.  List all artifacts from the Archaic Period",
            "4.  List artifact titles ordered by accession year descending",
            "5.  How many artifacts are there per department?",
            "6.  Which artifacts have more than 1 image?",
            "7.  What is the average rank of all artifacts?",
            "8.  Which artifacts have a higher colorcount than mediacount?",
            "9.  List all artifacts created between 1500 and 1600",
            "10. List artifact titles and hues for Byzantine culture",
            "11. List each artifact title with its associated hues",
            "12. Get artifact titles, cultures, and media ranks where the period is not null",
            "13. Find artifact titles ranked in the top 10 that include the hue 'Grey'",
            "14. How many artifacts exist per classification, and what is their average media count?",
            "15. How many artifacts have no media files?",
            "16. What are all distinct hues used?",
            "17. Top 5 most used colors by frequency",
            "18. What is the average coverage percentage for each hue?",
            "19. List all colors used for a given artifact ID",
            "20. What is the total number of color entries?",
            "21. Show artifacts where accession method contains 'purchase'",
            "22. List all artifacts from a specific department",
            "23. Find artifacts that have no description",
            "24. Show artifacts ordered by object ID",
            "25. Count artifacts with a non-null period"
        ]

        selected_query = st.selectbox("✨ Select a Pre-built Query", query_options)

        query = ""
        params = None
        run_query = False

        if selected_query != query_options[0]:
            if selected_query == query_options[19]:
                artifact_id = st.number_input("Enter Artifact ID", min_value=1, value=1)
                query = "SELECT color, hue, percent FROM artifact_colors WHERE objectid = %s;"
                params = (artifact_id,)
            elif selected_query == query_options[22]:
                department_name = st.text_input("Enter Department Name", value="Drawings")
                query = "SELECT id, title, culture FROM artifact_metadata WHERE department = %s;"
                params = (department_name,)

            if st.button("🚀 Run Query"):
                if selected_query == query_options[1]:
                    query = "SELECT * FROM artifact_metadata WHERE century='11th century' AND culture='Byzantine';"
                elif selected_query == query_options[2]:
                    query = "SELECT DISTINCT culture FROM artifact_metadata WHERE culture IS NOT NULL;"
                elif selected_query == query_options[3]:
                    query = "SELECT * FROM artifact_metadata WHERE period='Archaic';"
                elif selected_query == query_options[4]:
                    query = "SELECT title, accessionyear FROM artifact_metadata ORDER BY accessionyear DESC;"
                elif selected_query == query_options[5]:
                    query = "SELECT department, COUNT(*) as artifact_count FROM artifact_metadata GROUP BY department;"
                elif selected_query == query_options[6]:
                    query = "SELECT m.title FROM artifact_metadata m JOIN artifact_media md ON m.id = md.objectid WHERE md.imagecount > 1;"
                elif selected_query == query_options[7]:
                    query = "SELECT AVG(rank_value) as avg_rank FROM artifact_media;"
                elif selected_query == query_options[8]:
                    query = "SELECT m.title FROM artifact_metadata m JOIN artifact_media md ON m.id=md.objectid WHERE md.colorcount > md.mediacount;"
                elif selected_query == query_options[9]:
                    query = "SELECT * FROM artifact_metadata m JOIN artifact_media md on m.id = md.objectid WHERE md.datebegin BETWEEN 1500 AND 1600;"
                elif selected_query == query_options[10]:
                    query = "SELECT m.title, c.hue FROM artifact_metadata m JOIN artifact_colors c ON m.id=c.objectid WHERE m.culture='Byzantine';"
                elif selected_query == query_options[11]:
                    query = "SELECT m.title, GROUP_CONCAT(c.hue SEPARATOR ', ') as Hues FROM artifact_metadata m JOIN artifact_colors c ON m.id=c.objectid GROUP BY m.id, m.title;"
                elif selected_query == query_options[12]:
                    query = "SELECT title, culture, rank_value FROM artifact_metadata m JOIN artifact_media md ON m.id=md.objectid WHERE m.period IS NOT NULL;"
                elif selected_query == query_options[13]:
                    query = "SELECT m.title FROM artifact_metadata m JOIN artifact_media md ON m.id=md.objectid JOIN artifact_colors c ON m.id=c.objectid WHERE c.hue='Grey' ORDER BY md.rank_value DESC LIMIT 10;"
                elif selected_query == query_options[14]:
                    query = "SELECT classification, COUNT(*) as artifact_count, AVG(mediacount) as avg_media FROM artifact_metadata m JOIN artifact_media md ON m.id=md.objectid GROUP BY classification;"
                elif selected_query == query_options[15]:
                    query = "SELECT COUNT(*) as artifacts_no_media FROM artifact_media WHERE mediacount=0;"
                elif selected_query == query_options[16]:
                    query = "SELECT DISTINCT hue FROM artifact_colors;"
                elif selected_query == query_options[17]:
                    query = "SELECT color, COUNT(*) as frequency FROM artifact_colors GROUP BY color ORDER BY frequency DESC LIMIT 5;"
                elif selected_query == query_options[18]:
                    query = "SELECT hue, AVG(percent) as avg_percent FROM artifact_colors GROUP BY hue;"
                elif selected_query == query_options[20]:
                    query = "SELECT COUNT(*) as total_color_entries FROM artifact_colors;"
                elif selected_query == query_options[21]:
                    query = "SELECT * FROM artifact_metadata WHERE accessionmethod LIKE '%purchase%';"
                elif selected_query == query_options[23]:
                    query = "SELECT * FROM artifact_metadata WHERE description IS NULL;"
                elif selected_query == query_options[24]:
                    query = "SELECT * FROM artifact_metadata ORDER BY id;"
                elif selected_query == query_options[25]:
                    query = "SELECT COUNT(*) as artifacts_with_period FROM artifact_metadata WHERE period IS NOT NULL;"

                if query:
                    run_query = True

        if run_query and query:
            try:
                df_query = pd.read_sql(query, engine, params=params)
                st.success(f"✅ Query executed successfully! Rows returned: {len(df_query)}")
                st.dataframe(df_query)
            except Exception as e:
                st.error(f"Query failed: {e}")
