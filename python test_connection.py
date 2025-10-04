import mysql.connector

try:
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="thisisMaryam07",
        database="harvard_artifacts"
    )
    if connection.is_connected():
        print("Successfully connected to MySQL Database!")
    connection.close()

except mysql.connector.Error as e:
    print(f"Error connecting to MySQL Database: {e}")
