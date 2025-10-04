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
Clone this repository to your local machine.
```git clone https://github.com/NeoNethereal/Harvard-Artifact-Explorer.git cd Harvard-Artifact-Explorer```
