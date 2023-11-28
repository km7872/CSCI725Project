# Author: Parth Sethia
# Modified by: Katyani Mehra

import psycopg2
from datetime import date
import threading
import random
import time

local_thread_data = threading.local()


def make_connection():
    if not hasattr(local_thread_data, 'conn'):
        local_thread_data.conn = psycopg2.connect(
                host="localhost",
                database="AdvDB",
                user="postgres",
                password="RITPostGreSQL"
            )
    return local_thread_data.conn


def CreateAccount(username, password, firstName, lastName):
    successful_count = 0
    conn = make_connection()
    cur = conn.cursor()
    insert_query = 'insert into public.users (username, password, first_name, last_name) values (%s, %s, %s, %s)'
    try:
        cur.execute(insert_query, (username, password, firstName, lastName))
        conn.commit()
        successful_count = 1
    except:
        conn.rollback()
    return successful_count


def SubmitOrder(date, username, password, listOfProductsAndQuantities):
    total_products = len(listOfProductsAndQuantities)
    conn = make_connection()
    cur = conn.cursor()
    successful_count = 0
    check_cred = 'select * from public.users where username = %s and password = %s'
    cur.execute(check_cred, (username, password))
    result = cur.fetchall()
    try:
        if result:
            str_of_product_values = ', '.join(["({0}, {1})".format(values[0], values[1]) for values in listOfProductsAndQuantities])
            check_items_availability = 'select p1.* from public.products p1 ' \
                                          'join ( ' \
                                          'select * from ( values {0} ) as z (product_id, quantity) ' \
                                          ') as p2 ' \
                                          'on p1.id = p2.product_id ' \
                                          'where p1.quantity >= p2.quantity'.format(str_of_product_values)

            cur.execute(check_items_availability)
            if cur.rowcount == total_products:
                update_query = 'update public.products p1 set quantity = p1.quantity - p2.quantity ' \
                               'from (select * from ( values {0} ) as z (product_id, quantity) ' \
                               ') as p2 where p1.id = p2.product_id ' \
                               'and p1.quantity >= p2.quantity'.format(str_of_product_values)
                cur.execute(update_query)

                insert_query_orders = 'insert into public.orders ("user", date) values (%s, %s) returning id'
                cur.execute(insert_query_orders, (username, date.today()))
                order_id = cur.fetchone()[0]

                str_of_product_values_with_ids = ', '.join(["({2}, {0}, {1})".format(values[0], values[1], order_id) for values in listOfProductsAndQuantities])
                insert_query_items = 'insert into public.items (order_id, product_id, product_quantity) values {0}'.format(str_of_product_values_with_ids)
                cur.execute(insert_query_items)
                conn.commit()
                successful_count = 1
    except:
        conn.rollback()
    return successful_count


def PostReview(username, password, productID, rating, reviewText):
    successful_count = 0
    conn = make_connection()
    cur = conn.cursor()
    check_cred = 'select * from public.users where username = %s and password = %s'
    cur.execute(check_cred, (username, password))
    result = cur.fetchall()
    if result:
        insert_query = 'insert into public.reviews (reviews_description, reviews_rating, date, "user", product_id) values' \
                       '(%s, %s, %s, %s, %s)'
        try:
            cur.execute(insert_query, (reviewText, rating, date.today(), username, productID))
            conn.commit()
            successful_count = 1
        except:
            conn.rollback()
    return successful_count


def AddProduct(name, description, price, initialStock):
    successful_count = 0
    conn = make_connection()
    cur = conn.cursor()
    insert_query = 'insert into public.products (name, description, price, quantity) values (%s, %s, %s, %s)'
    try:
        cur.execute(insert_query, (name, description, price, initialStock))
        conn.commit()
        successful_count = 1
    except:
        conn.rollback()
    return successful_count


def UpdateStockLevel(productID, itemCountToAdd):
    successful_count = 0
    conn = make_connection()
    cur = conn.cursor()
    update_query = 'update public.products set quantity = quantity + %s where id = %s'
    try:
        cur.execute(update_query, (itemCountToAdd, productID))
        rows = cur.rowcount
        if rows == 0:
            successful_count = 0
        else:
            successful_count = 1
        conn.commit()
    except:
        conn.rollback()
    return successful_count


def GetProductAndReviews(productID):
    successful_count = 0
    rows = None
    conn = make_connection()
    cur = conn.cursor()
    select_query = 'select p.*, r."user", r.reviews_rating, r.reviews_description from public.products p ' \
                   'inner join public.reviews r ' \
                   'on p.id = r.product_id ' \
                   'where r.product_id = %s'
    try:
        cur.execute(select_query, (productID,))
        rows = cur.fetchall()[0]
        successful_count = 1
    except:
        pass
    return successful_count, rows

def GetAverageUserRating(username):
    successful_count = 0
    avg_rating = None
    conn = make_connection()
    cur = conn.cursor()
    select_query = 'select sum(reviews_rating), count("user") from public.reviews ' \
                   'where "user" = %s ' \
                   'group by "user"'
    try:
        cur.execute(select_query, (username, ))
        result = cur.fetchall()
        avg_rating = result[0][0]/result[0][1]
        successful_count = 1
    except:
        pass
    return successful_count, avg_rating

def run_test(start_time, results):
    successful_count_from_thread = 0
    if not hasattr(local_thread_data, 'count'):
        local_thread_data.count = 0
    # local_thread_data.count = 0
    while True:
        if time.time() - start_time >= 300:
            # print("local thread count ",local_thread_data.count)
            results.append(local_thread_data.count)
            break
            # return local_thread_data.count
        operation = random.choices(
            ["CreateAccount", "AddProduct", "SubmitOrder", "PostReview", "UpdateStockLevel", "GetProductAndReviews",
             "GetAverageUserRating"],
            [0.03, 0.02, 0.10, 0.05, 0.10, 0.65, 0.05],
            k=1
        )[0]

        if operation == "CreateAccount":
            username = "user" + str(random.randint(1, 100000))
            password = "password"
            successful_count_from_thread += CreateAccount(username, password, "FirstName", "LastName")

        elif operation == "AddProduct":
            product_name = "Product"+str(random.randint(1, 100000))
            quantity = random.randint(0, 50)
            successful_count_from_thread += AddProduct(product_name, "Description", 19.99, quantity)

        elif operation == 'PostReview':
            username = "user" + str(random.randint(1, 100000))
            password = "password"
            conn = make_connection()
            cur = conn.cursor()
            cur.execute('select id from public.products')
            result = cur.fetchall()
            product_id_list = [row[0] for row in result]
            product_id = random.choice(product_id_list)
            rating = random.uniform(1.0, 5.0)
            reviewText = "Random review text" + str(random.randint(1, 100000))
            successful_count_from_thread += PostReview(username, password, product_id, rating, reviewText)

        elif operation == 'UpdateStockLevel':
            conn = make_connection()
            cur = conn.cursor()
            cur.execute('select id from public.products')
            result = cur.fetchall()
            product_id_list = [row[0] for row in result]
            product_id = random.choice(product_id_list)
            successful_count_from_thread += UpdateStockLevel(product_id, random.randint(1, 100))

        elif operation == 'GetProductAndReviews':
            conn = make_connection()
            cur = conn.cursor()
            cur.execute('select id from public.products')
            result = cur.fetchall()
            product_id_list = [row[0] for row in result]
            product_id = random.choice(product_id_list)
            count, rows = GetProductAndReviews(product_id)
            successful_count_from_thread += count

        elif operation == 'GetAverageUserRating':
            username = "user" + str(random.randint(1, 100000))
            count, rating_avg = GetAverageUserRating(username)
            successful_count_from_thread += count

        elif operation == 'SubmitOrder':
            username = "user" + str(random.randint(1, 100000))
            password = 'password'
            conn = make_connection()
            cur = conn.cursor()
            cur.execute('select id from public.products')
            result = cur.fetchall()
            product_id_list = [row[0] for row in result]
            listOfProductsAndQuantities = [(random.choice(product_id_list), random.randint(1, 5)) for i in range(10)]
            successful_count_from_thread += SubmitOrder(date.today(), username, password, listOfProductsAndQuantities)

        local_thread_data.count = successful_count_from_thread

def get_count():
    return local_thread_data.count

def main(n_o_t):
    num_of_threads = n_o_t
    threads = []
    start_time = time.time()
    results = []
    for i in range(num_of_threads):
        thread = threading.Thread(target=run_test, args=(start_time,results))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    total_successful_count = sum(results)

    conn = psycopg2.connect(
                host="localhost",
                database="AdvDB",
                user="postgres",
                password="RITPostGreSQL"
            )
    cur = conn.cursor()
    cur.execute('select sum(public.products.quantity)/count(public.products.quantity) as A from public.products '
                'where quantity < 0')
    rows = cur.fetchone()
    print("Number of threads used:", num_of_threads)
    print("Percentage of products with a stock level less than zero measured at the end of the test:", rows[0])
    print("Total successful operations:", total_successful_count)

if __name__ == '__main__':
    for i in range(1, 11):
        main(i)
