from flask import Flask, jsonify
from flask_cors import CORS
import psycopg2
import os 
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

def get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
        )
        print("Connected to PostgreSQL!")
        return conn
    except Exception as e:
        print("Failed to connect to PostgreSQL:", e)
        return None

# New route to fetch products
@app.route("/products", methods=["GET"])
def get_products():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM products;")
    products = cur.fetchall()
    cur.close()
    conn.close()

    # Format the data for JSON response
    products_list = []
    for product in products:
        products_list.append({
            "id": product[0],          # id
            "asin": product[1],        # asin
            "name": product[2],        # name
            "retailer": product[3],    # retailer
            "price": float(product[4]) if product[4] is not None else None,  # price
            "sales_rank": product[5],  # sales_rank
            "last_updated": product[6].isoformat() if product[6] else None,  # last_updated
            "cost_price": float(product[7]) if product[7] is not None else None,  # cost_price
            "sale_price": float(product[12]) if product[12] is not None else None,  # sale_price (index 12!)
            "profit": float(product[8]) if product[8] is not None else None,  # profit
            "estimated_sales": product[9],  # estimated_sales
            "source_url": product[10],  # source_url
            "amazon_url": product[11],  # amazon_url
            "profit_margin": float(product[13]) if product[13] is not None else None  # profit_margin
        })


    return jsonify(products_list)


@app.route("/winners", methods=["GET"])
def get_winners():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.name, w.amazon_price, w.lowest_competitor_price
        FROM winners w
        JOIN products p ON w.product_id = p.id
        WHERE w.sales_rank < 10000
        ORDER BY w.price_difference DESC;
    """)
    winners = cur.fetchall()
    cur.close()
    conn.close()

    # Format the data for JSON response
    winners_list = []
    for winner in winners:
        winners_list.append({
            "product_name": winner[0],
            "amazon_price": winner[1],
            "competitor_price": winner[2]
        })

    return jsonify(winners_list)

if __name__ == "__main__":
    app.run(debug=True)