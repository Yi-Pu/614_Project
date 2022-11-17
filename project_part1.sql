/* Group members:
Yining Sun, Nikita Tcherevik, Yi Pu
*/

/* Within our database table schema, we identified four entities, the first is the actual hospital itself, 
the second is the hospital’s geographic location, the third is a hospital’s weekly statistics, 
and the fourth one is the hospital’s quality ratings over time.  
We chose them because the attributes across these different entities share a lot of similar information, 
of which our decided primary key would help point us to all the needed information. 
For example, the primary key of the latitude and longitude tells us all about related geographic variables such as state and zipcode. 
The actual hospital itself is evidently its own entity that contains relevant information such as the name, 
the type of hospital and its ownership, and whether it contains emergency services. 
Note that these are “static” attributes of a hospital, 
so it makes sense for this to be stored within one table which can then have a 1-to-1 relationship with geographic info, 
and 1-to-many info on weekly statistics and quality entities. Note that now that we found a way to store hospital metadata, 
this cuts out a lot of the redundant information as these two can just be referenced by their relevant IDs when we are looking at weekly statistics or quality ratings, 
which are related in their own separate ways and should be considered as their own entities..*/

/* This is the table categorizing the geographic information of each hospital */
CREATE TABLE geographic_info(
geocoded_hospital_address TEXT PRIMARY KEY,
zip TEXT,
city TEXT,
fips_code TEXT,
state CHAR(2),
address TEXT
);
/*This next table references the hospital basic metadata */
CREATE TABLE hospital_basic_info (
hospital_pk TEXT PRIMARY KEY,
name TEXT NOT NULL,
geocoded_hospital_address TEXT
REFERENCES geographic_info,
type TEXT,
emergency_services BOOLEAN DEFAULT FALSE
);
/* Table holding the weekly statistic entities of hospitals */
CREATE TABLE hospital_capacity (
hospital_pk TEXT 
REFERENCES hospital_basic_info,
date DATE,
all_adult_hospital_beds_7_day_avg INTEGER
CHECK (all_adult_hospital_beds_7_day_avg > 0),
all_pediatric_inpatient_beds_7_day_avg INTEGER
CHECK (all_pediatric_inpatient_beds_7_day_avg > 0),
all_adult_hospital_inpatient_bed_occupied_7_day_coverage INTEGER
CHECK (all_adult_hospital_inpatient_bed_occupied_7_day_coverage > 0),
all_pediatric_inpatient_bed_occupied_7_day_avg INTEGER
CHECK (all_pediatric_inpatient_bed_occupied_7_day_avg > 0),
total_icu_beds_7_day_avg INTEGER
CHECK (total_icu_beds_7_day_avg > 0),
icu_beds_used_7_day_avg INTEGER
CHECK (icu_beds_used_7_day_avg > 0),
inpatient_beds_used_covid_7_day_avg INTEGER
CHECK (inpatient_beds_used_covid_7_day_avg > 0),
staffed_adult_icu_patients_confirmed_covid_7_day_avg INTEGER
CHECK (staffed_adult_icu_patients_confirmed_covid_7_day_avg > 0),
PRIMARY KEY (hospital_pk, date)
);
/* Table holding the different Quality entities */
CREATE TABLE quality_rating (
facility_id TEXT REFERENCES hospital_basic_info (hospital_pk),
year CHAR(4) NOT NULL,
hospital_overall_rating INTEGER,
PRIMARY KEY (facility_id, year)
);
