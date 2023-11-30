# Author: Katyani Mehra

import psycopg2
import postgres_test


def read_file(filename):
    script = ''
    with open(filename) as f:
        for l in f:
            script+=l
    return script

def main():
    conn = postgres_test.create_connection()
    script = read_file("droptablesscript.txt")
    print(script)
    cursor = conn.cursor()
    cursor.execute(script)
    script = read_file("postgres_table_scripts.txt")
    print(script)
    cursor = conn.cursor()
    cursor.execute(script)

    print('Tables created')

    # Fetch all rows from table

    cursor.execute("SELECT * FROM products;")
    rows = cursor.fetchall()

    # Print all rows

    for row in rows:
        print(
            "Data row = (%s, %s, %s,%s,%s)" % (str(row[0]), str(row[1]), str(row[2]), str(row[2]), str(row[3])))
    cursor.close()
    conn.close()


if __name__ == '__main__':
    main()