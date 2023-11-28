# Author: Parth Sethia
# Modified by: Katyani Mehra

import sys

from flask import Flask, render_template, request, redirect, url_for, session
import psycopg2

app = Flask(__name__)
app.secret_key = 'secret_key'

conn = psycopg2.connect(
        host="localhost",
        database="AdvDB",
        user="postgres",
        password="RITPostGreSQL"
    )

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/createAccount')
def createAccountPage():
    # print("b ",success_message)
    # success_message = request.args.get('success_message')
    success_message = session.pop('success_message', None)
    if success_message:
        return render_template('createAccount.html', success_message=success_message)
    else:
        return render_template('createAccount.html')

@app.route('/updateStock')
def updateStockPage():
    success_message_update_stock = session.pop('success_message_update_stock', None)
    if success_message_update_stock:
        return render_template('updateStock.html', success_message=success_message_update_stock)
    else:
        return render_template('updateStock.html')

@app.route('/updateStockCode', methods = ['POST'])
def updateStock():
    product_id_from_form = request.form.get('productid')
    stock_to_add_from_form = int(request.form.get('stocktoadd'))
    cur = conn.cursor()
    select_query = 'select quantity from public.products where id = %s'
    cur.execute(select_query, (product_id_from_form, ))
    rows = cur.fetchall()
    if not rows:
        success_message_update_stock = 'Product ID not found'
        session['success_message_update_stock'] = success_message_update_stock
        return redirect(url_for('updateStockPage'))
    if stock_to_add_from_form < 0:
        success_message_update_stock = 'Please enter a positive stock number'
        session['success_message_update_stock'] = success_message_update_stock
        return redirect(url_for('updateStockPage'))
    curr_stock = int(rows[0][0])
    update_query = 'update public.products set quantity = %s where id = %s'
    cur.execute(update_query, (stock_to_add_from_form+curr_stock, product_id_from_form))
    conn.commit()
    # cur.close()
    success_message_update_stock = 'Updated the inventory successfully'
    session['success_message_update_stock'] = success_message_update_stock
    return redirect(url_for('updateStockPage'))


@app.route('/addProduct')
def addProductPage():
    success_message_add_product = session.pop('success_message_add_product', None)
    if success_message_add_product:
        return render_template('addProduct.html', success_message = success_message_add_product)
    else:
        return render_template('addProduct.html')

@app.route('/addProductCode', methods=['POST'])
def addProd():
    product_name_from_form = request.form.get('productname')
    product_description_from_form = request.form.get('productdescription')
    product_price_from_form = int(request.form.get('productprice'))
    product_stock_from_form = int(request.form.get('productstock'))
    if product_stock_from_form < 0:
        success_message_add_product = 'Please enter positive stock number'
        session['success_message_add_product'] = success_message_add_product
        return redirect(url_for('addProductPage'))
    if product_price_from_form < 0:
        success_message_add_product = 'Please enter positive price'
        session['success_message_add_product'] = success_message_add_product
        return redirect(url_for('addProductPage'))
    cur = conn.cursor()
    insert_query = 'insert into public.products (name, description, price, quantity) values (%s, %s, %s, %s)'
    cur.execute(insert_query, (product_name_from_form, product_description_from_form, product_price_from_form, product_stock_from_form))
    conn.commit()
    # cur.close()
    success_message_add_product = 'Product successfully added'
    session['success_message_add_product'] = success_message_add_product
    return redirect(url_for('addProductPage'))


@app.route('/register', methods=['POST'])
def registration():
    # print(request.form.get('username'))
    username_from_form = request.form.get('username')
    password_from_form = request.form.get('password')
    firstName_from_form = request.form.get('firstName')
    lastName_from_form = request.form.get('lastName')
    cur = conn.cursor()
    query = 'select username from public.users where username = %s'
    cur.execute(query,(username_from_form,))
    rows = cur.fetchall()
    print(rows)
    if rows:
        # cur.close()
        success_message = "Username already exists! Choose a different username"
        session['success_message'] = success_message
        return redirect(url_for('createAccountPage'))
    else:
        insert_query = 'insert into public.users (username, password, first_name, last_name) values (%s, %s, %s, %s)'
        cur.execute(insert_query, (username_from_form, password_from_form, firstName_from_form, lastName_from_form))
        conn.commit()
        # cur.close()
        success_message = "Form submitted successfully!"
        session['success_message'] = success_message
        return redirect(url_for('createAccountPage'))
    # return render_template('createAccount.html', success_message=success_message)


if __name__ == "__main__":
    app.run(debug=True)