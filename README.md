🚓 SecureCheck: Traffic Stop Analysis

SecureCheck is a Streamlit dashboard that analyzes traffic stop data using PostgreSQL and SQL queries. It helps explore driver demographics, violation patterns, and enforcement trends.

⚙️ Features

Store and query traffic stop data in PostgreSQL

Run interactive SQL queries (predefined + custom)

Explore demographics, violations, and arrest/search trends

Generate traffic stop summaries with user input

📂 Project Files

main.py → Streamlit app

requirements.txt → Dependencies

cleaned_traffic_stop.csv → Dataset

SecureCheck_min1.ipynb → Preprocessing & analysis notebook

🛠️ Setup
git clone https://github.com/your-username/SecureCheck.git
cd SecureCheck

python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows

pip install -r requirements.txt

Database

Install PostgreSQL and start server

Create database:

CREATE DATABASE traffic;


Update DB URL in main.py if needed:

postgresql://<username>:<password>@localhost:5432/traffic

Run App
streamlit run main.py

📊 Example Insights

Top vehicles in drug-related stops

Age groups with highest arrest rates

Time of day with most stops

Violations linked to searches/arrests

📑 Dataset

Driver demographics

Stop details (time, duration, location)

Search & arrest indicators

Violation types
