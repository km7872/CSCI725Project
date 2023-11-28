# Author: Parth Sethia
# Modified by: Katyani Mehra

import sys

import psycopg2
from datetime import date, timedelta
import random
import threading
import postgres_test

def make_connection():
    if not hasattr(local_thread_data, 'conn'):
        # local_thread_data.conn = psycopg2.connect(
        #         host="localhost",
        #         database="AdvDB",
        #         user="postgres",
        #         password="RITPostGreSQL"
        #     )
        local_thread_data.conn = postgres_test.create_connection()
    return local_thread_data.conn

def add_products():
    conn = make_connection()
    cur = conn.cursor()
    count = 0
    lst = [i for i in range(1, 1001)]
    while count != 1000:  # Add 1000 random products
        id = lst[0]
        product_name = "Product" + str(id)
        description = "Description" + str(id)
        price = random.uniform(10.0, 100.0)
        quantity = random.randint(0, 50)
        insert_query = 'insert into products (name, description, price, quantity) values (%s, %s, %s, %s)'
        try:
            cur.execute(insert_query, (product_name, description, price, quantity))
            conn.commit()
            count+=1
            lst.pop(0)
        except Exception as e:
            conn.rollback()
            print(f"Error adding product: {e}")
    print('{0} products created'.format(count))


def create_accounts():
    conn = make_connection()
    cur = conn.cursor()
    count=0
    lst = [i for i in range(1,1001)]
    while count!=1000:
        id = lst[0]
        username = "user" + str(id)
        password = "password"
        first_name = "Jane"
        last_name = "Doe"
        insert_query = 'insert into users (username, password, first_name, last_name) values (%s, %s, %s, %s)'
        try:
            cur.execute(insert_query, (username, password, first_name, last_name))
            count += 1
            conn.commit()
            lst.pop(0)
        except Exception as e:
            conn.rollback()
            print(f"Error creating account: {e}")
    print('{0} users created'.format(count))


def post_reviews():
    conn = make_connection()
    cur = conn.cursor()
    count = 0
    cur.execute('select id from products')
    result = cur.fetchall()
    product_id_list = [row[0] for row in result]
    # print(product_id_list)
    # print(type(product_id_list))
    while count != 20000:
        username = "user" + str(random.randint(1, 1000))
        product_id = random.choice(product_id_list)
        rating = random.uniform(1.0, 5.0)
        review_text = "Random review text"
        insert_query = 'insert into reviews (reviews_description, reviews_rating, date, "user", product_id) ' \
                       'values (%s, %s, %s, %s, %s)'
        try:
            cur.execute(insert_query, (review_text, rating, date.today(), username, product_id))
            conn.commit()
            count+=1
        except Exception as e:
            conn.rollback()
            print(f"Error posting review: {e}")
    print('{0} reviews created'.format(count))


# Function to submit random past orders without stock decrement
def submit_past_orders():
    conn = make_connection()
    cur = conn.cursor()
    count = 0
    cur.execute('select id from products')
    result = cur.fetchall()
    product_id_list = [row[0] for row in result]
    # product_id = random.choice(product_id_list)
    while count != 10000:
        username = "user" + str(random.randint(1, 1000))
        order_date = date.today() - timedelta(days=random.randint(1, 365))
        product_quantities = [(random.choice(product_id_list), random.randint(1, 5)) for i in range(10)]

        insert_order_query = 'insert into orders ("user", date) values (%s, %s) returning id'


        try:
            cur.execute(insert_order_query, (username, order_date))
            order_id = cur.fetchone()[0]
            order_values = ", ".join(["(%s, %s, %s)" % (order_id, product_id, quantity) for product_id, quantity in product_quantities])
            insert_items_query = 'insert into items (order_id, product_id, product_quantity) values {0}'.format(order_values)
            # print(insert_items_query)
            cur.execute(insert_items_query, (order_id, order_values))
            conn.commit()
            count+=1
        except Exception as e:
            conn.rollback()
            print(f"Error submitting past order: {e}")
    print('{0} orders created'.format(count))


if __name__ == "__main__":
    local_thread_data = threading.local()
    add_products()
    create_accounts()
    post_reviews()
    submit_past_orders()
