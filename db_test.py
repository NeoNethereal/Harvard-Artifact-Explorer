import toml
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError


print("Attempting to read secrets.toml file...")

try:
    # 
    secrets = toml.load(".streamlit/secrets.toml")
    db_secrets = secrets['database']
    
    user = db_secrets['db_user']
    password = db_secrets['db_pass']
    host = db_secrets['db_host']
    dbname = db_secrets['db_name']
    
    print("Successfully read credentials from file.")
    
    # g
    conn_string = f"mysql+mysqlconnector://{user}:{password}@{host}/{dbname}"
    
    print("Connecting to the database...")
    
    # C
    engine = create_engine(conn_string)
    connection = engine.connect()
    
    print("\n✅ ✅ ✅ --- CONNECTION SUCCESSFUL --- ✅ ✅ ✅")
    
    connection.close()

except FileNotFoundError:
    print("\n❌ ❌ ❌ --- ERROR --- ❌ ❌ ❌")
    print("Could not find the '.streamlit/secrets.toml' file. Make sure it's in the correct location.")

except KeyError as e:
    print("\n❌ ❌ ❌ --- ERROR --- ❌ ❌ ❌")
    print(f"A key is missing or misspelled in your secrets.toml file. The missing key is: {e}")

except SQLAlchemyError as e:
    print("\n❌ ❌ ❌ --- DATABASE ERROR --- ❌ ❌ ❌")
    print("An error occurred while trying to connect to the database.")
    print("The full error message is:")
    print(e)

except Exception as e:
    print("\n❌ ❌ ❌ --- AN UNEXPECTED ERROR OCCURRED --- ❌ ❌ ❌")
    print("The full error message is:")
    print(e)
