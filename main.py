import streamlit as st
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine, inspect



traffic_df=pd.read_csv("data\cleaned_traffic_stop.csv")

db_url = "postgresql://postgres:Admin@localhost:5432/traffic"
engine=create_engine(db_url)

# Creating New Table and storing the cleaned data into SQL
traffic_df.to_sql('traffic_stop',engine,index=False,if_exists='replace') 

# SQL QUERIES :(Medium level):

queries = { 
    #1.What are the top 10 vehicle_Number involved in drug-related stops?
    "Top 10 vehicles involved in drug-related stops":
        """
        SELECT vehicle_number,COUNT(drugs_related_stop) AS drug_related_stop_count
        FROM traffic_stop WHERE drugs_related_stop=TRUE
        GROUP BY vehicle_number
        ORDER BY drug_related_stop_count DESC LIMIT 10;
        """,
    #2.Which vehicles were most frequently searched?
    "Most frequently searched violations":
        """
        SELECT violation_raw, COUNT(violation_raw) AS search_count 
        FROM traffic_stop WHERE search_conducted='TRUE' 
        GROUP BY violation_raw 
        ORDER BY search_count DESC LIMIT 10;
        """,
    #4.Which driver age group had the highest arrest rate?
    "Driver age groups with highest arrest rates":
        """
        SELECT driver_age_raw, COUNT(is_arrested) AS arrest_count 
        FROM traffic_stop WHERE is_arrested= TRUE 
        GROUP BY driver_age_raw 
        ORDER BY arrest_count DESC LIMIT 10;
        """,
    #5.What is the gender distribution of drivers stopped in each country?
    "Gender distribution of drivers stopped in each country":
        """
        SELECT country_name,driver_gender,COUNT(driver_gender) AS gender_count 
        FROM traffic_stop 
        GROUP BY country_name,driver_gender 
        ORDER BY country_name,gender_count DESC;
        """,
    # 6.Which race and gender combination has the highest search rate?
    "Race and Gender Combination with the Highest Search Rate":
        """
        SELECT driver_race,driver_gender,COUNT(search_conducted) AS search_count 
        FROM traffic_stop 
        WHERE search_conducted=TRUE 
        GROUP BY driver_race,driver_gender 
        ORDER BY search_count DESC LIMIT 10;
        """,
    # 7.What time of day sees the most traffic stops?
    "Time of Day with the Highest Number of Traffic Stops":
        """
        SELECT EXTRACT(HOUR FROM stop_date_time::timestamp) AS hour_of_day_24Hr, stop_time_12Hr AS hour_min_in_12Hr_format, COUNT(*) AS stop_count
        FROM traffic_stop
        GROUP BY hour_of_day_24Hr,hour_min_in_12Hr_format
        ORDER BY stop_count DESC
        LIMIT 20;
        """,
    # 8.What is the average stop duration for different violations?
    "Average Stop Duration by Violation Type":
        """
        SELECT violation_raw,
        ROUND(AVG(CASE stop_duration
               WHEN '0-15' THEN 7.5
               WHEN '16-30' THEN 23
               WHEN '30+' THEN 35
               END),2) AS avg_stop_duration
        FROM traffic_stop
        GROUP BY violation_raw
        ORDER BY avg_stop_duration DESC;
        """,
    # 9.Are stops during the night more likely to lead to arrests?
    "Likelihood of Arrests During Night-Time Traffic Stops":
        """
        SELECT CAST(EXTRACT(HOUR FROM stop_date_time::timestamp) AS INT) AS hour_of_day, stop_time_12Hr AS hour_min_in_12Hr_format, COUNT(is_arrested) AS arrest_count
        FROM traffic_stop
        WHERE is_arrested = TRUE
        GROUP BY hour_of_day,hour_min_in_12Hr_format
        ORDER BY arrest_count DESC
        LIMIT 10;
        """,
    # 10.Which violations are most associated with searches or arrests?
    "Violations Most Commonly Associated with Searches or Arrests":
        """
        SELECT
        violation_raw,
        COUNT(*) AS total_stops_with_search_and_arrest
        FROM traffic_stop
        WHERE search_conducted = TRUE AND is_arrested = TRUE
        GROUP BY violation_raw
        ORDER BY total_stops_with_search_and_arrest DESC;
        """,
    # 11.Which violations are most common among younger drivers (<25)?
    "Most Common Violations Among Drivers Under 25":
        """
        SELECT violation_raw,
        COUNT(violation_raw) AS violation_count
        FROM traffic_stop
        WHERE driver_age_raw<25
        GROUP BY violation_raw
        ORDER BY violation_count DESC;
        """,
    # 12.Is there a violation that rarely results in search or arrest?
    "Violations That Rarely Lead to Searches or Arrests":
        """
        SELECT violation_raw,COUNT(*) AS total_stops_without_search_or_arrest
        FROM traffic_stop
        WHERE search_conducted = FALSE AND is_arrested = FALSE
        GROUP BY violation_raw
        ORDER BY total_stops_without_search_or_arrest ASC;
        """,
    # 13.Which countries report the highest rate of drug-related stops?
    "Countries with the Highest Rate of Drug-Related Traffic Stops":
        """
        SELECT country_name, COUNT(drugs_related_stop) AS drug_related_stop_count
        FROM traffic_stop
        WHERE drugs_related_stop = TRUE
        GROUP BY country_name
        ORDER BY drug_related_stop_count DESC;
        """,
    # 14.What is the arrest rate by country and violation?
    "Arrest Rate by Country and Type of Violation":
        """
        SELECT country_name, violation_raw, ROUND(AVG(CASE WHEN is_arrested = TRUE THEN 1.0 ELSE 0 END) * 100, 2)AS arrest_rate
        FROM traffic_stop
        GROUP BY country_name, violation_raw
        ORDER BY arrest_rate DESC;
        """,
    # 15.Which country has the most stops with search conducted?
    "Country with the Highest Number of Stops Involving a Search":
        """
        SELECT country_name, COUNT(search_conducted) AS search_count
        FROM traffic_stop
        WHERE search_conducted = TRUE
        GROUP BY country_name
        ORDER BY search_count DESC LIMIT 1;
        """,
    #SQL queries(Complex):
    #1.Yearly Breakdown of Stops and Arrests by Country (Using Subquery and Window Functions)
    "Yearly Breakdown of Stops and Arrests by Country":
        """
        WITH yearly_summary AS
        (SELECT 
        country_name,
		EXTRACT(YEAR FROM stop_date_time::date) AS year,
		COUNT(is_arrested) AS total_stops,
		SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) AS arrest_count
		FROM traffic_stop
		GROUP BY country_name, EXTRACT(YEAR FROM stop_date_time::date))
        SELECT country_name,year,total_stops,arrest_count,SUM(arrest_count) OVER (PARTITION BY country_name ORDER BY year) AS cumulative_arrest_count 
        FROM yearly_summary;
        """,
    #2.Driver Violation Trends Based on Age and Race (Join with Subquery)
    "Driver Violation Trends by Age and Race":
        """
        SELECT ts.driver_age_raw, ts.driver_race, COUNT(*) AS count_race 
        FROM (SELECT driver_age_raw, driver_race FROM traffic_stop WHERE driver_age_raw IS NOT NULL AND driver_race IS NOT NULL) AS ts 
        GROUP BY ts.driver_age_raw, ts.driver_race
        ORDER BY ts.driver_age_raw, count_race;
        """,
    #3.Time Period Analysis of Stops (Joining with Date Functions) , Number of Stops by Year,Month, Hour of the Day
    # #Cast method is used the slice the decimal value
    "Time Period Analysis of Stops: Number of Stops by Year, Month, and Hour":
        """
        SELECT 
        CAST(EXTRACT(YEAR FROM stop_date::date) AS INT) AS stop_year, 
        CAST(EXTRACT(MONTH FROM stop_date::date) AS INT) AS stop_month, 
        CAST(EXTRACT(HOUR FROM stop_date_time::timestamp) AS INT) AS stop_hour,
        COUNT(*) AS total_stops
        FROM traffic_stop 
        GROUP BY CAST(EXTRACT(YEAR FROM stop_date::date) AS INT), 
        CAST(EXTRACT(MONTH FROM stop_date::date) AS INT), 
        CAST(EXTRACT(HOUR FROM stop_date_time::timestamp) AS INT)
        ORDER BY stop_year, stop_month, stop_hour;
        """,
    #4.Violations with High Search and Arrest Rates (Window Function)
    "Violations with Highest Search and Arrest Rates":
        """
        SELECT violation_raw, COUNT(violation_raw) AS total_violation_raw_count,
        SUM(CASE WHEN search_conducted = TRUE THEN 1 ELSE 0 END) AS search_count,
        SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) AS arrest_count,
        ROUND(AVG(CASE WHEN search_conducted = TRUE THEN 1.0 ELSE 0 END) * 100, 2) AS search_avg_rate,
        ROUND(AVG(CASE WHEN is_arrested = TRUE THEN 1.0 ELSE 0 END) * 100, 2) AS arrest_avg_rate
        FROM traffic_stop
        GROUP BY violation_raw
        ORDER BY search_count DESC, arrest_count DESC, search_avg_rate DESC, arrest_avg_rate DESC;
        """,
    #5.Driver Demographics by Country (Age, Gender, and Race)
    "Driver Demographics by Country: Age, Gender, and Race":
        """
        SELECT country_name,
        ROUND(AVG(driver_age_raw)) AS avg_age,
        COUNT(*) AS total_stops,
        SUM(CASE WHEN driver_gender = 'M' THEN 1 ELSE 0 END) AS male_count,
        SUM(CASE WHEN driver_gender = 'F' THEN 1 ELSE 0 END) AS female_count,
        SUM(CASE WHEN driver_race = 'White' THEN 1 ELSE 0 END) AS white_count,
        SUM(CASE WHEN driver_race = 'Black' THEN 1 ELSE 0 END) AS black_count,
        SUM(CASE WHEN driver_race = 'Hispanic' THEN 1 ELSE 0 END) AS hispanic_count,
        SUM(CASE WHEN driver_race = 'Asian' THEN 1 ELSE 0 END) AS asian_count,
        SUM(CASE WHEN driver_race = 'Other' THEN 1 ELSE 0 END) AS other_race_count
        FROM traffic_stop
        GROUP BY country_name
        ORDER BY total_stops DESC;
        """,
    #6.Top 5 Violations with Highest Arrest Rates
    "Top 5 Violations with the Highest Arrest Rates":
        """
        SELECT violation_raw,
        COUNT(is_arrested) AS total_stops,
        SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) AS arrest_count,
        ROUND(AVG(CASE WHEN is_arrested = TRUE THEN 1.0 ELSE 0 END) * 100, 2) AS arrest_avg_rate
        FROM traffic_stop
        GROUP BY violation_raw
        ORDER BY arrest_avg_rate DESC
        LIMIT 5;
        """
}

# Streamlit UI
st.set_page_config(page_title="SecureCheck Traffic Analysis", page_icon="🚨", layout="wide")

#Heading
st.markdown("""
    <div style="background-color:#002C54; padding: 25px; border-radius: 12px; margin-top: 0px; box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
        <h1 style="color: #FFDC00; text-align:center;">🚓 SecureCheck: Traffic Stop Analysis</h1>
        <p style="color:#ffffff; text-align:center;">An interactive SQL-Powered Dashboard</p>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")


st.markdown("""
    <div style="background-color:#e0f7fa; padding: 20px; border-radius: 10px; margin-top: 20px;">
        <h2 style="color:#0074D9;">📊 Advanced SQL-Powered Insights</h2>
        <p style="color:#333;">Explore the data visually and interactively.</p>
    </div>
""", unsafe_allow_html=True)


options = ["--📋Available Queries!--"] + list(queries)

# Create dropdown with default index 0 (placeholder)

selected_query = st.selectbox("🔍 Choose a query to uncover insights.", options, index=0)

# Only run query if real selection is made
if selected_query !="--📋Available Queries!--":
    query = queries[selected_query]
    result_df = pd.read_sql(query, engine)
    st.badge("Query executed.", icon=":material/check:", color="green")
    st.dataframe(result_df)
    

#--------------------------------------------------------------------------------------

# Load the dataset


# Title
st.markdown("""
    <div style="background-color:#f0f8ff; padding: 20px; border-radius: 10px; margin-top: 30px;">
        <h2 style="color:#0074D9;">📝 Generate a Custom Traffic Stop Summary</h2>
        <p style="color:#333;">Fill in details to generate a narrative summary.</p>
    </div>
""", unsafe_allow_html=True)


# User Inputs
age = st.number_input("Driver Age", min_value=16, max_value=100, step=1)
gender = st.selectbox("Driver Gender", ["Male", "Female"])
violation = st.selectbox("Violation",["Drunk Driving","Speeding","Seatbelt","Signal Violation","Others"])
stop_time = st.text_input("Stop Time")
search_conducted = st.radio("Was a search conducted?", ["Yes", "No"])
stop_outcome = st.selectbox("Stop Outcome", ["Ticket", "Warning", "Arrest"])
stop_duration = st.selectbox("Stop Duration", ["0-15", "16-30", "30+"])
drug_related = st.radio("Was it drug-related?", ["Yes", "No"])

if st.button("Generate Summary"):

    # Convert inputs to match dataset format
    gender_short = 'M' if gender == 'Male' else 'F'
    search_flag = True if search_conducted == 'Yes' else False
    drug_flag = True if drug_related == 'Yes' else False

    # Filter the dataset
    filtered_df = traffic_df[
        (traffic_df['driver_age_raw'] == age) &
        (traffic_df['driver_gender'] == gender_short) &
        (traffic_df['violation_raw'].str.lower() == violation.lower()) &
        (traffic_df['stop_time_12hr'].str.lower() == stop_time.lower()) &
        (traffic_df['search_conducted'] == search_flag) &
        (traffic_df['stop_outcome'].str.lower() == stop_outcome.lower()) &
        (traffic_df['stop_duration'] == stop_duration) &
        (traffic_df['drugs_related_stop'] == drug_flag)
    ]

    # Generate summary
    if not filtered_df.empty:
        row = filtered_df.iloc[0]
        summary = (
            f"A {row['driver_age_raw']}-year-old {'male' if row['driver_gender'] == 'M' else 'female'} driver was stopped for "
            f"{row['violation_raw']} at {row['stop_time_12hr']}. "
            f"{'A search was conducted' if row['search_conducted'] else 'No search was conducted'}, "
            f"and the driver received a {row['stop_outcome'].lower()}. "
            f"The stop lasted {row['stop_duration']} minutes and was "
            f"{'drug-related' if row['drugs_related_stop'] else 'not drug-related'}."
        )
        st.info(summary)
        st.dataframe(filtered_df)
        st.badge("📂 Here is your matching results!", icon=":material/check:", color="green")
    else:
        st.markdown(":orange-badge[🗃️ No entries match your filters..]")
 
    # Display the result

   
