# This scipts is to load CMS quality data

import psycopg
import credentials

conn = psycopg.connect(
    host="sculptor.stat.cmu.edu", dbname=credentials.DB_USER,
    user=credentials.DB_USER, password=credentials.DB_PASSWORD
)

cur = conn.cursor()

# Set initital values
big_data_set = []
num_rows_inserted = 0

# make a new transaction
with conn.transaction():
    for row in big_data_set:
        try:
            # make a new SAVEPOINT -- like a save in a video game
            with conn.transaction():
                # perhaps a bunch of reformatting
                # and data manipulation goes here

                # now insert the data
                cur.execute("INSERT INTO foo ...", ...)
        except Exception:
            # if an exception/error happens in this block,
            # Postgres goes back to the last savepoint upon
            # exiting the `with` block
            print("insert failed")
            # add additional logging, error handling here
        else:
            # no exception happened, so we continue
            # without reverting the savepoint
            num_rows_inserted += 1

# now we commit the entire transaction
conn.commit()

# Now the block is done and committed. But if there was an exception raised in
# the block that was not caught, the context manager would automatically call
# conn.rollback() for us.
