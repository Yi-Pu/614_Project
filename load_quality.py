'''This script adds hospital quality ratings to the database and updates ownership, emergency services and type'''

import psycopg
import credentials
import pandas as pd
import sys


def process_csv(file):
    '''This function processes and cleans the new csv of hospital quality ratings
    
       Parameters:

       file: The csv file path
    '''
    quality_data = pd.read_csv(file)

    quality_data.loc[quality_data['Emergency Services'] == "Yes", 'Emergency Services'] = "TRUE"
    quality_data.loc[quality_data['Emergency Services'] == "No", 'Emergency Services'] = "FALSE"
    quality_data.loc[quality_data['Hospital overall rating'] == "Not Available", 'Hospital overall rating'] = "null"
    
    return quality_data


def add_to_database(file, date):
    '''Inputs the necessary data from the csv into the database
    
       Parameters:

       file: A Pandas Dataframe of the CSV
       date: Date of when the quality ratings were recorded
    '''

    conn = psycopg.connect(
    host="sculptor.stat.cmu.edu", dbname=credentials.DB_USER,
    user=credentials.DB_USER, password=credentials.DB_PASSWORD)

    cur = conn.cursor()

    num_rows_inserted = 0
    num_hospitals_inserted = 0
    discard = pd.DataFrame(columns=file.columns)

    check = pd.read_sql_query("SELECT hospital_pk FROM hospital_basic_info", conn)
    comparison = set(check.hospital_pk.unique())

    with conn.transaction():
        for index, row in file.iterrows():
            try:
                with conn.transaction():
                    cur.execute(
                        "INSERT INTO hospital_basic_info (hospital_pk, name, type, ownership_type, emergency_services)"
                        "VALUES (%s, %s, %s, %s, %s)"
                        "ON CONFLICT(hospital_pk) DO UPDATE SET"
                        "(type, ownership_type, emergency_services) = (EXCLUDED.type, EXCLUDED.ownership_type, EXCLUDED.emergency_services)",
                        (row['Facility ID'], row['Facility Name'],
                        row['Hospital Type'], row['Hospital Ownership'],
                        row['Emergency Services'])
                    )

                    if row['Facility ID'] not in comparison:
                        num_hospitals_inserted += 1

                    if row['Hospital overall rating'] == "null":
                        cur.execute(
                            "INSERT INTO quality_rating (facility_id, date)"
                            "VALUES (%s, to_date(%s, 'YYYY-MM-DD'))", 
                            (row["Facility ID"], date))
                    else:
                        cur.execute(
                            "INSERT INTO quality_rating (facility_id, date, hospital_overall_rating)"
                            "VALUES (%s, to_date(%s, 'YYYY-MM-DD'), %s)", 
                            (row["Facility ID"], date, row['Hospital overall rating']))
                    
            except Exception as e:
                print("insert failed")
                print("row " + str(index) + " failed.")
                discard = discard.append(row)
            else:
                num_rows_inserted += 1
    conn.commit()

    discardFile = "quality_discard-" + date + ".csv"
    print("The number of quality ratings added: " + str(num_rows_inserted))
    print("Number of Hospitals Inserted: " + str(num_hospitals_inserted))
    discard.to_csv(discardFile, index=False)
    return


def main():
    date = sys.argv[1]
    file = sys.argv[2]
    quality_data = process_csv(file)
    add_to_database(quality_data, date)


if __name__ == "__main__":
    main()
