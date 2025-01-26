# PostgreSQL Setup Documentation

This document outlines the steps taken to set up and access PostgreSQL for the **Price Comparison App** project.

---

## **1. Install PostgreSQL**

### **On macOS (using Homebrew)**

1. Install Homebrew (if not already installed):

   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. Install PostgreSQL:

   ```bash
   brew install postgresql@15
   ```

3. Start the PostgreSQL service:

   ```bash
   brew services start postgresql@15
   ```

4. Verify the installation:
   ```bash
   psql --version
   ```

---

## **2. Access PostgreSQL**

### **Default Behavior**

By default, Homebrew installs PostgreSQL with your system username as the superuser. To access PostgreSQL, use:

```bash
psql -U your_username -d postgres
```

Replace `your_username` with your actual system username (e.g., `lalmonte`).

---

### **Create the `postgres` Role (Optional)**

If you prefer to use the `postgres` role, follow these steps:

1. Access PostgreSQL as a superuser:

   ```bash
   psql -U your_username -d postgres
   ```

2. Create the `postgres` role:

   ```sql
   CREATE ROLE postgres WITH SUPERUSER LOGIN;
   ```

3. Set a password for the `postgres` role:

   ```sql
   ALTER ROLE postgres WITH PASSWORD 'your_password';
   ```

4. Exit the PostgreSQL CLI:

   ```sql
   \q
   ```

5. Verify the `postgres` role:
   ```bash
   psql -U postgres
   ```

---

## **3. Create a New Database**

1. Access PostgreSQL:

   ```bash
   psql -U your_username -d postgres
   ```

2. Create a new database:

   ```sql
   CREATE DATABASE price_comparison;
   ```

3. Switch to the new database:
   ```sql
   \c price_comparison;
   ```

---

## **4. Set Up Tables**

### **Products Table**

This table stores raw product data from all retailers.

```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    upc TEXT NOT NULL,
    retailer TEXT NOT NULL,
    price DECIMAL NOT NULL,
    sales_rank INT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **Winners Table**

This table stores the results of the analysis (products where Amazon's price is higher than competitors but has a good sales rank).

```sql
CREATE TABLE winners (
    id SERIAL PRIMARY KEY,
    product_id INT REFERENCES products(id),
    amazon_price DECIMAL NOT NULL,
    lowest_competitor_price DECIMAL NOT NULL,
    competitor_retailer TEXT NOT NULL,
    sales_rank INT,
    price_difference DECIMAL NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## **5. Insert Sample Data**

1. Insert sample products:

   ```sql
   INSERT INTO products (name, upc, retailer, price, sales_rank)
   VALUES
       ('Product A', '123456789012', 'Amazon', 100.00, 5000),
       ('Product A', '123456789012', 'Walmart', 80.00, NULL),
       ('Product B', '987654321098', 'Amazon', 150.00, 3000),
       ('Product B', '987654321098', 'Target', 120.00, NULL);
   ```

2. Query the data:
   ```sql
   SELECT * FROM products;
   ```

---

## **6. Connect PostgreSQL to Flask Backend**

1. Install `psycopg2` (PostgreSQL adapter for Python):

   ```bash
   pip install psycopg2
   ```

2. Update your Flask app (`app.py`) to connect to the PostgreSQL database:

   ```python
   from flask import Flask, jsonify
   import psycopg2

   app = Flask(__name__)

   def get_db_connection():
       conn = psycopg2.connect(
           dbname="price_comparison",
           user="your_username",  # Replace with your PostgreSQL username
           password="your_password",  # Replace with your PostgreSQL password
           host="localhost",
           port="5432"
       )
       return conn

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
   ```

3. Test the backend:
   ```bash
   python app.py
   ```
   Visit `http://127.0.0.1:5000/winners` in your browser to see the JSON response.

---

## **7. Next Steps**

1. **Populate the Database**:
   - Write scripts to scrape or fetch product data from retailers and insert it into the `products` table.
2. **Automate the Analysis**:
   - Write a script to compare prices and populate the `winners` table.
3. **Deploy the Backend**:
   - Deploy your Flask app and PostgreSQL database to a cloud platform like Heroku, Render, or AWS.

---

## **Troubleshooting**

- **Role Does Not Exist**: If you encounter the error `role "postgres" does not exist`, use your system username to access PostgreSQL:
  ```bash
  psql -U your_username -d postgres
  ```
- **Database Does Not Exist**: If the database doesn’t exist, create it:
  ```sql
  CREATE DATABASE your_database_name;
  ```

---

This document provides a clear and concise reference for setting up and accessing PostgreSQL for your project. Let me know if you need further assistance! 🚀
