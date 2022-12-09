# This is to test the streamlit app

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import psycopg
import plotly.express as px


st.markdown("# Hospital Data Weekly Report")


conn = psycopg.connect(
    host="sculptor.stat.cmu.edu", dbname="yinings",
    user="yinings", password="shai0Asho")
cur = conn.cursor()

# 1
st.markdown("### A summary of how many hospital records were loaded in the most recent week, \
and how that compares to previous weeks")

cur.execute("SELECT date, COUNT(date) FROM hospital_capacity "
            "GROUP BY date "
            # compare with previous 10 weeks
            "HAVING date >= (max(date) - 10 * integer '7')"
            "ORDER BY date DESC")
num_records = cur.fetchall()
st.write(num_records[0][1],
         "hospital records were loaded in the most recent week (",
         num_records[0][0], ").")
for i in range(1, len(num_records)):
    if num_records[i][1] < num_records[0][1]:
        st.write(
            "There were", num_records[i][1],
            "hospital records loaded in the week of",
            num_records[i][0], ";")
        st.write("The number of records loaded this week is",
                 num_records[0][1]-num_records[i][1],
                 "more than the week of", num_records[i][0], ".")
    if num_records[i][1] == num_records[0][1]:
        st.write(
            "There were", num_records[i][1],
            "hospital recordsloaded in the week of",
            num_records[i][0], ";")
        st.write("The number of records loaded this week is same as the week of",
                 num_records[i][0], ".")
    if num_records[i][1] > num_records[0][1]:
        st.write(
            "There were", num_records[i][1],
            "hospital records loaded in the week of",
            num_records[i][0], ";")
        st.write("The number of records loaded this week is",
                 num_records[i][1]-num_records[0][1],
                 "less than the week of", num_records[i][0], ".")


# 2
st.markdown("### A table summarizing the number of adult and pediatric beds \
available this week, the number used, and the number used by patients with COVID, \
    compared to the 4 most recent weeks")

cur.execute(
    "SELECT date, sum(all_adult_hospital_beds_7_day_avg) AS sum_adult,"
    "sum(all_pediatric_inpatient_beds_7_day_avg) AS sum_pediatric, "
    "sum(all_adult_hospital_inpatient_bed_occupied_7_day_coverage) AS sum_adult_used, "
    "sum(all_pediatric_inpatient_bed_occupied_7_day_avg) AS sum_pediatric_used, "
    "sum(inpatient_beds_used_covid_7_day_avg) as sum_covid_used "
    "FROM hospital_capacity "
    "GROUP BY date "
    "HAVING date >= (max(date) - 4 * integer '7') "
    "ORDER BY date DESC")
capacity_records = pd.DataFrame(cur.fetchall(),
                                columns=['date', 'adult beds available',
                                         'pediatric beds available',
                                         'adult beds used',
                                         'pediatric beds used',
                                         'beds used by patients with COVID'])

capacity_records.insert(loc=2,
                        column='difference between adult beds available',
                        value=pd.to_numeric(capacity_records.iloc[0, 1]
                                            - capacity_records.iloc[:, 1]))
capacity_records.insert(loc=4,
                        column='difference between pediatric beds available',
                        value=pd.to_numeric(capacity_records.iloc[0, 3]
                                            - capacity_records.iloc[:, 3]))
capacity_records.insert(loc=6,
                        column='difference between adult beds used',
                        value=pd.to_numeric(capacity_records.iloc[0, 5]
                                            - capacity_records.iloc[:, 5]))
capacity_records.insert(loc=8,
                        column='difference between pediatric beds used',
                        value=pd.to_numeric(capacity_records.iloc[0, 7]
                                            - capacity_records.iloc[:, 7]))
capacity_records.insert(loc=10,
                        column='difference between the beds used by patients with COVID',
                        value=pd.to_numeric(capacity_records.iloc[0, 9]
                                            - capacity_records.iloc[:, 9]))

st.dataframe(capacity_records)


# 3
st.markdown("### A table and a plot summarizing the fraction of beds currently in \
use by hospital quality rating")

pro = pd.read_sql_query(
    "SELECT a.hospital_overall_rating, "
    "AVG(b.all_adult_hospital_inpatient_bed_occupied_7_day_coverage/b.all_adult_hospital_beds_7_day_avg) AS adult_beds_occupied_proportion, "
    "AVG(b.all_pediatric_inpatient_bed_occupied_7_day_avg/b.all_pediatric_inpatient_beds_7_day_avg) AS pediatric_beds_occupied_proportion, "
    "AVG(b.icu_beds_used_7_day_avg/b.total_icu_beds_7_day_avg) AS icu_beds_occupied_proportion"
    " FROM hospital_capacity AS b"
    " JOIN quality_rating AS a"
    " ON a.facility_id = b.hospital_pk"
    " WHERE b.all_adult_hospital_beds_7_day_avg > 0"
    " AND b.all_pediatric_inpatient_beds_7_day_avg > 0"
    " AND b.total_icu_beds_7_day_avg > 0"
    " GROUP BY a.hospital_overall_rating"
    " ORDER BY a.hospital_overall_rating DESC;", conn)
pro.iloc[0, 0] = "Not Available"
st.dataframe(pro)

st.set_option('deprecation.showPyplotGlobalUse', False)
plt.title("matplotlib plot")
pro.plot.barh(x='hospital_overall_rating', color="ryb",
              xlabel="hospital overall rating", ylabel="fraction of beds in used")
st.pyplot()


# 4
st.markdown("### A table and a plot of the total number of hospital beds used per week, \
over all time, split into all cases and COVID cases")

beds = pd.read_sql_query(
    "SELECT date, "
    "SUM(all_adult_hospital_inpatient_bed_occupied_7_day_coverage+ \
        all_pediatric_inpatient_bed_occupied_7_day_avg) "
    "AS all_cases_beds_used_per_week, "
    "SUM(inpatient_beds_used_covid_7_day_avg) "
    "AS COVID_cases_beds_used_per_week FROM hospital_capacity "
    "GROUP BY date "
    "ORDER BY date", conn)

st.dataframe(beds)

# create figure and axis objects with subplots()
fig, ax = plt.subplots()
# twin object for two different y-axis on the sample plot
ax2=ax.twinx()
# make a plot
ax.plot(
        list(beds.date.apply(lambda x: str(x))),
        beds['all_cases_beds_used_per_week'],
        color='orange', 
        marker="o")
# set x-axis label
ax.set_xlabel("year", fontsize=14)
# set y-axis label
ax.set_ylabel("All cases",
              color='orange',
              fontsize=14)
# Rotate x-sticks
# make a plot with different y-axis using second axis object
ax2.plot(
    list(beds.date.apply(lambda x: str(x))),
    beds['covid_cases_beds_used_per_week'],
    color='purple',
    marker="o")
ax2.set_ylabel("Covid cases", color='purple', fontsize=14)
fig.autofmt_xdate()
st.pyplot()


# 5
st.markdown("### A table of the hospitals with the largest changes \
in COVID cases in the last week")
st.markdown("hospitals with most increase:")
increase_most = pd.read_sql_query(
    "SELECT j.name, i.address, j.changes \
    FROM geographic_info AS i \
    JOIN( \
    SELECT hospital_basic_info.facility_id, \
    hospital_basic_info.name, \
    change_info.changes \
    FROM hospital_basic_info \
    JOIN( \
    SELECT latest_week.hospital_pk, \
    latest_week.inpatient_beds_used_covid_7_day_avg-second_latest_week.inpatient_beds_used_covid_7_day_avg AS changes \
    FROM \
    (SELECT a.hospital_pk, a.inpatient_beds_used_covid_7_day_avg \
    FROM hospital_capacity AS a \
    WHERE a.date = (SELECT MAX(date) FROM hospital_capacity) \
    AND a.inpatient_beds_used_covid_7_day_avg >= 0) AS latest_week \
    JOIN \
    (SELECT a.date, a.hospital_pk, a.inpatient_beds_used_covid_7_day_avg \
    FROM hospital_capacity AS a \
    WHERE a.date = (SELECT MAX(date) FROM hospital_capacity \
    WHERE date < (SELECT MAX(date) FROM hospital_capacity)) \
    AND a.inpatient_beds_used_covid_7_day_avg >= 0 \
    ) AS second_latest_week \
    ON latest_week.hospital_pk = second_latest_week.hospital_pk \
    ORDER BY changes DESC \
    ) AS change_info \
    ON hospital_basic_info.facility_id = change_info.hospital_pk \
    ) AS j \
    ON i.hospital_pk = j.facility_id \
    LIMIT 10", conn)
st.dataframe(increase_most)

st.markdown("hospitals with most decrease:")
decrease_most = pd.read_sql_query(
    "SELECT j.name, i.address, j.changes \
    FROM geographic_info AS i \
    JOIN( \
    SELECT hospital_basic_info.facility_id, \
    hospital_basic_info.name, \
    change_info.changes \
    FROM hospital_basic_info \
    JOIN( \
    SELECT latest_week.hospital_pk, \
    latest_week.inpatient_beds_used_covid_7_day_avg-second_latest_week.inpatient_beds_used_covid_7_day_avg AS changes \
    FROM \
    (SELECT a.hospital_pk, a.inpatient_beds_used_covid_7_day_avg \
    FROM hospital_capacity AS a \
    WHERE a.date = (SELECT MAX(date) FROM hospital_capacity) \
    AND a.inpatient_beds_used_covid_7_day_avg >= 0) AS latest_week \
    JOIN \
    (SELECT a.date, a.hospital_pk, a.inpatient_beds_used_covid_7_day_avg \
    FROM hospital_capacity AS a \
    WHERE a.date = (SELECT MAX(date) FROM hospital_capacity \
    WHERE date < (SELECT MAX(date) FROM hospital_capacity)) \
    AND a.inpatient_beds_used_covid_7_day_avg >= 0 \
    ) AS second_latest_week \
    ON latest_week.hospital_pk = second_latest_week.hospital_pk \
    ORDER BY changes \
    ) AS change_info \
    ON hospital_basic_info.facility_id = change_info.hospital_pk \
    ) AS j \
    ON i.hospital_pk = j.facility_id \
    LIMIT 10", conn)
st.dataframe(decrease_most)


# 6
st.markdown("### A map showing the number of COVID cases by state")

map = pd.read_sql_query(
    "select geographic_info.state,"
    " (sum(hospital_capacity.inpatient_beds_used_covid_7_day_avg) "
    " + sum(hospital_capacity.staffed_icu_adult_patients_confirmed_covid_7_day_avg))*7 as covid_numbers"
    " from hospital_capacity inner join geographic_info"
    " on hospital_capacity.hospital_pk = geographic_info.hospital_pk"
    " group by geographic_info.state", conn)

fig = px.choropleth(
    map,
    locations='state',
    color='covid_numbers',
    color_continuous_scale='spectral_r',
    hover_name='state',
    locationmode='USA-states',
    labels={'covid_numbers': 'COVID Cases'},
    scope='usa')

fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
st.plotly_chart(fig)


# 7
st.markdown("### A table of the states in which the number of cases has increased \
by the most since last week")

most_increases = pd.read_sql_query(
    "select state, cast((covid_numbers - prev_week) AS INTEGER) as change_in_cases from "
    "(select geographic_info.state, hospital_capacity.date, \
        (sum(hospital_capacity.inpatient_beds_used_covid_7_day_avg) \
            + sum(hospital_capacity.staffed_icu_adult_patients_confirmed_covid_7_day_avg))*7 \
                as covid_numbers, \
                    lag((sum(hospital_capacity.inpatient_beds_used_covid_7_day_avg) \
                        + sum(hospital_capacity.staffed_icu_adult_patients_confirmed_covid_7_day_avg))*7, 1) \
                            over (PARTITION BY geographic_info.state \
                                ORDER BY hospital_capacity.date) as prev_week, "
    "rank() over (PARTITION BY geographic_info.state ORDER BY hospital_capacity.date DESC) as rnk "
    " from hospital_capacity inner join geographic_info on hospital_capacity.hospital_pk = geographic_info.hospital_pk"
    " group by geographic_info.state, hospital_capacity.date) as df where rnk = 1 \
    and (covid_numbers - prev_week) > 0 ORDER BY change_in_cases DESC", conn).reset_index().drop(['index'], axis=1).set_index(['state'])

st.dataframe(most_increases)

conn.close()
