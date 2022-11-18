'''This script adds HHS data to the database
 and updates geographic_info, hospital_capacity
 and hospital_basic_info'''

import psycopg
import credentials
import pandas as pd
from datetime import datetime
import numpy as np
import sys


def process_csv(file):
    '''This function processes and cleans the csv of HHS data

       Parameters:

       file: The csv file path
    '''
    hhs_df = pd.read_csv(file)

    # Data wrangling
    hhs_df.replace(-999999, np.nan)
    hhs_df["collection_week"] = \
        hhs_df.collection_week.apply(
        lambda x: datetime.strptime(str(x), '%d/%m/%Y'))
    hhs_df["geocoded_hospital_address"] = \
        hhs_df.geocoded_hospital_address.apply(lambda x: str(x))
    hhs_df["zip"] = hhs_df.zip.apply(lambda x: str(x))
    hhs_df["city"] = hhs_df.city.apply(lambda x: str(x))
    hhs_df["fips_code"] = hhs_df.fips_code.apply(lambda x: str(x))
    hhs_df["state"] = hhs_df.state.apply(lambda x: str(x))
    hhs_df["address"] = hhs_df.address.apply(lambda x: str(x))

    return hhs_df


def add_to_database(file):
    '''Inputs the necessary data from the csv into the database

       Parameters:

       file: A Pandas Dataframe of the CSV
    '''

    conn = psycopg.connect(
        host="sculptor.stat.cmu.edu", dbname=credentials.DB_USER,
        user=credentials.DB_USER, password=credentials.DB_PASSWORD)

    cur = conn.cursor()

    # Data to be checked
    discard = pd.DataFrame(columns=file.columns)

    # Initial count
    num_rows_inserted = 0

    with conn.transaction():
        for index, row in file.iterrows():
            try:
                with conn.transaction():
                    # Update geographic_info
                    cur.execute(
                        "INSERT INTO geographic_info (geocoded_hospital_address, \
                            zip, city, fips_code, state, address)"
                        "VALUES (%s, %s, %s, %s, %s, %s)"
                        "ON CONFLICT(geocoded_hospital_address) DO UPDATE SET"
                        "(zip, city, fips_code, state, address) = \
                            (EXCLUDED.zip, EXCLUDED.city, \
                            EXCLUDED.fips_code, EXCLUDED.state, \
                            EXCLUDED.address)",
                        (row['geocoded_hospital_address'],
                         row['zip'], row['city'], row['fips_code'],
                         row['state'], row['address']))

                    # Update hospital_capacity
                    cur.execute(
                        "INSERT INTO hospital_capacity (hospital_pk, date, \
                        all_adult_hospital_beds_7_day_avg, \
                        all_pediatric_inpatient_beds_7_day_avg, \
                        all_adult_hospital_inpatient_bed_occupied_7_day_coverage, \
                        all_pediatric_inpatient_bed_occupied_7_day_avg, \
                        total_icu_beds_7_day_avg, \
                        icu_beds_used_7_day_avg, \
                        inpatient_beds_used_covid_7_day_avg, \
                        staffed_icu_adult_patients_confirmed_covid_7_day_avg)"
                        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        (row['hospital_pk'],
                         row['collection_week'],
                         row['all_adult_hospital_beds_7_day_avg'],
                         row['all_pediatric_inpatient_beds_7_day_avg'],
                         row['all_adult_hospital_inpatient_bed_occupied_7_day_coverage'],
                         row['all_pediatric_inpatient_bed_occupied_7_day_avg'],
                         row['total_icu_beds_7_day_avg'],
                         row['icu_beds_used_7_day_avg'],
                         row['inpatient_beds_used_covid_7_day_avg'],
                         row['staffed_icu_adult_patients_confirmed_covid_7_day_avg']))

                    # Update hospital_basic_info
                    cur.execute(
                        "INSERT INTO hospital_basic_info \
                        (hospital_pk, name, geocoded_hospital_address, type)"
                        "VALUES(%s, %s, %s, %s)"
                        "ON CONFLICT (hospital_pk) DO UPDATE SET"
                        "(name, geocoded_hospital_address, type) = \
                        (EXCLUDED.name, EXCLUDED.geocoded_hospital_address, \
                        EXCLUDED.type)",
                        (row['hospital_pk'], row['hospital_name'],
                         row['address'], row['hospital_subtype']))

            except Exception as e:
                print(e)
                print("insert failed")
                print("row " + str(index) + " failed.")
                discard = discard.append(row)
            else:
                num_rows_inserted += 1

    conn.commit()

    discardFile = "hhs_discard.csv"
    print("The number of rows added: " + str(num_rows_inserted))
    discard.to_csv(discardFile, index=False)
    return


def main():
    file = sys.argv[1]
    hhs_df = process_csv(file)
    add_to_database(hhs_df)


if __name__ == "__main__":
    main()
