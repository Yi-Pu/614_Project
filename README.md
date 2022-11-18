# 614_Project
NOTE: We have slightly changed the schema from when we submitted Part 1 to fix some of the checks we had because we didn't notice how some of the columns would have zeros in hospital_capacity

In order to load the data, first make sure that the new CSV and the scripts are in the same directory. NOTE: They don't have to necessarily be in the same directory, but if they are not, you must include the whole path to the csv so that the script can access them.

After you configured the data to be with the python script, go into terminal and go to the directory that the python script is in.

In order to load a new batch of HHS data, run the following command:

python load_hhs.py <Name of new HHS CSV>
  
In order to load a new batch of Quality data, run the following command:
  
python load_quality.py <date of collection in YYYY-MM-DD format> <Name of new quality CSV>
  
For both of the files, there will be the following print output:

Number of new rows of data added
Number of new hospitals added
  
Furthermore, in the case of invalid rows of data:

It will print the row that failed in the console
That row will be stored in a new CSV so that it can be fixed and then re-loaded.
