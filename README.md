# Harvard-Artifact-Explorer
An interactive, end-to-end data exploration platform using the Harvard Art Museums public API and Streamlit.

## 🏛 Harvard Artifact Explorer
This project provides an interactive, end-to-end data exploration platform using the Harvard Art Museums public API. It's built to empower users to dynamically collect, store, and query rich art collections through a simple and intuitive Streamlit web application.

## ✨ Key Features
- ETL Pipeline: Fetches up to 12,500 artifact records from the Harvard Art Museum API, transforms the raw JSON data, and stores it in a structured MySQL database.

- Database Integration: Automatically creates and populates three relational tables—artifact_metadata, artifact_media, and artifact_colors—without requiring manual SQL setup.

- Dynamic Data Exploration: Through a Streamlit dashboard, users can select different artifact classifications to fetch and insert data in real-time.

- Interactive Query Workspace: The app includes a ready-to-use SQL workspace with over 25 predefined queries. This allows users to analyze the collected data in real-time and explore various aspects of the art collection.

- Secure Configuration: All sensitive information, such as the MySQL credentials and API keys, is managed securely using Streamlit's secrets.toml file.

## 🚀 Getting Started
Follow these steps to set up and run the application on your local machine.

### Prerequisites
You need to have the following software installed:

- Python 3.10+

- MySQL Database (and the MySQL service running)

- Git

### Step 1: Clone the Repository
Clone this repository to your local machine:

`git clone https://github.com/NeoNethereal/Harvard-Artifact-Explorer.git`

Navigate to the project folder:

`cd Harvard-Artifact-Explorer`

### Step 2: Install Dependencies
Navigate to the project directory and install the necessary Python libraries.

`pip install -r requirements.txt`

### Step 3: Configure Your Secrets
- To connect to the database and the Harvard API, you must set up a `secrets.toml` file.

- Create a new folder named `.streamlit` in the project's root directory.

- Inside the `.streamlit` folder, create a new file named `secrets.toml`.

- Copy and paste the following content into the file, replacing the placeholder values with your own MySQL credentials.

```
[mysql]
host="127.0.0.1"
user="root"
password="your_mysql_password"
database="harvard_artifacts"

[harvard]
api_key="your_harvard_api_key"
```

### Step 4: Run the Application
From the project's root directory, start the Streamlit application using your terminal.

`streamlit run project.py`

The application will automatically open in your default web browser at `http://localhost:8501`.
