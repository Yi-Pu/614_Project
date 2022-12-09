# 614_Project
NOTE: We have slightly changed the schema from when we submitted Part 1 to fix some of the checks we had because we didn't notice how some of the columns would have zeros in hospital_capacity.

First, make sure to establish the schema by loading the necessary data tables, which are detailed in project_part1.sql. Without these tables, the data will fail to generate.

In order to load the data, first make sure that the new CSV and the scripts are in the same directory. NOTE: They don't have to necessarily be in the same directory, but if they are not, you must include the whole path to the csv so that the script can access them.

After you configured the data to be with the python script, go into terminal and go to the directory that the python script is in.

In order to load a new batch of HHS data, run the following command:

python load_hhs.py <Name of new HHS CSV>

An example of this is: python load_hhs.py 2022-10-14-hhs-data.csv
  
In order to load a new batch of Quality data, run the following command:
  
python load_quality.py <date of collection in YYYY-MM-DD format> <Name of new quality CSV>

An example of this is: python load_quality.py 2022-10-15 Hospital_General_Information-2022-10.csv
  
For both of the files, there will be the following print output:

Number of new rows of data added
Number of new hospitals added
  
Furthermore, in the case of invalid rows of data:

It will print the row that failed in the console
That row will be stored in a new CSV so that it can be fixed and then re-loaded.

Once a new batch of data has been loaded, a dashboard can be generated that summarizes some key takeaways. The statistics included in this are:

1. A summary of how many hospital records were loaded in the most recent week,and how that compares to previous weeks.
2. A table summarizing the number of adult and pediatric beds available this week, the number used, and the number used by patients with COVID, compared to the 4 most recent weeks.
3. A table and a plot summarizing the fraction of beds currently in use by hospital quality rating.
4. A table and a plot of the total number of hospital beds used per week, over all time, split into all cases and COVID cases.
5. A table of the hospitals with the largest changes in COVID cases in the last week.
6. A map showing the total number of COVID cases by state.
7. A table of the states in which the number of cases has increased by the most since last week

In order to generate this dashboard, once the data is loaded, go into the directory that contains the Python scripts in the terminal of your computer. Once there, run the following command:

streamlit run dashboard_generation.py

This will generate a report with the most updated statistics from the new batch.
