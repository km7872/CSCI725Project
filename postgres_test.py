# Author: Katyani Mehra

import psycopg2

# host = "csci725group3postgres.postgres.database.azure.com"
# dbname = "postgres"
# user = "userpostgres@csci725group3postgres"
# password = "csci725@group3"
# sslmode = "require"

host = "c-postgres-cosmos-demo.hmzytyr5uzreih.postgres.cosmos.azure.com"
dbname = "citus"
user = "citus"
password = "csci725@group3"
sslmode = "require"

# Construct connection string

def create_connection():
    conn_string = "host={0} user={1} dbname={2} password={3} sslmode={4}".format(host, user, dbname, password, sslmode)
    conn = psycopg2.connect(conn_string)
    # print("Connection established")
    return conn


def main():
    create_connection()

if __name__ == '__main__':
    main()