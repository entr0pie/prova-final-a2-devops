from flask import Flask, jsonify
import redis
import requests
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

PRODUCT_API_URL = os.getenv('PRODUCT_API_URL')

DATABASE_HOST = os.getenv('DATABASE_HOST')
DATABASE_USER = os.getenv('DATABASE_USER')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')
DATABASE_SCHEMA = os.getenv('DATABASE_SCHEMA')

REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = int(os.getenv('REDIS_PORT'))

app = Flask(__name__)
cache = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)

@app.route('/order')
def create_order():
    cached = cache.get('product')
    if cached:
        product = eval(cached)
    else:
        r = requests.get(PRODUCT_API_URL + '/products')
        product = r.json()['products'][0]
        cache.set('product', str(product))

    db = mysql.connector.connect(
        host=DATABASE_HOST,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD,
        database=DATABASE_SCHEMA
    )
    cursor = db.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS orders (id INT AUTO_INCREMENT PRIMARY KEY, product_id INT, quantity INT, total_price INT)")
    cursor.execute("INSERT INTO orders (product_id, quantity, total_price) VALUES (%s, %s, %s)", (product['id'], 2, product['price'] * 2))
    db.commit()
    cursor.close()
    db.close()

    return jsonify({
        "order_id": 101,
        "product_id": product['id'],
        "quantity": 2,
        "total_price": product['price'] * 2
    })

def main():
    app.run(host='0.0.0.0', port=3002)
