🚓 SecureCheck: Traffic Stop Analysis

An interactive Streamlit-powered dashboard for analyzing traffic stop data using PostgreSQL and SQL queries.
The project enables users to explore traffic stop patterns, driver demographics, and enforcement trends with both predefined queries and custom filters.

📂 Project Structure
├── main.py                        # Streamlit application
├── requirements.txt               # Python dependencies
├── cleaned_traffic_stop.csv       # Preprocessed dataset
├── Mini_project_1(Secure_Check).ipynb  # Jupyter notebook for data preprocessing & analysis
├── .gitignore                     # Ignored files and folders

⚙️ Features

Store and query traffic stop data in PostgreSQL

Execute medium and advanced SQL queries interactively

Explore driver demographics, violation patterns, and arrest trends

Generate a custom traffic stop summary with user-provided details

Clean and organized dashboard UI

🛠️ Installation & Setup
1. Clone the Repository
git clone https://github.com/your-username/SecureCheck.git
cd SecureCheck

2. Create a Virtual Environment
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows

3. Install Dependencies
pip install -r requirements.txt

4. Setup PostgreSQL Database

Install PostgreSQL and start the server.

Create a database named traffic:

CREATE DATABASE traffic;


Update the connection string in main.py if needed:

db_url = "postgresql://<username>:<password>@localhost:5432/traffic"

5. Run the Application
streamlit run main.py

📊 Example Queries

The dashboard includes several predefined queries, such as:

Top 10 vehicles involved in drug-related stops

Driver age groups with highest arrest rates

Time of day with most traffic stops

Violations most associated with searches or arrests

Yearly breakdown of arrests by country

📑 Dataset

File: cleaned_traffic_stop.csv

Contains preprocessed records of traffic stops, including:

Driver demographics (age, gender, race)

Stop details (time, duration, location)

Search and arrest indicators

Violation types

📜 License

This project is licensed under the MIT License – free to use and modify