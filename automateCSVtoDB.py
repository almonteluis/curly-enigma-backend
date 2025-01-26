import csv
import psycopg2

# Database connection details
db_config = {
    'dbname': 'price_comparison',  # Your database name
    'user': 'lalmonte',            # Your PostgreSQL username
    'password': 'password123',   # Your PostgreSQL password
    'host': 'localhost',           # Your database host
    'port': '5432'                 # Your database port
}

# Path to your CSV file
csv_file = '/Users/lalmonte/Documents/Projects/Active/FBA Sourcing/Buy List.csv'
# List of required columns (those with NOT NULL constraints)
required_columns = [
    'product_name',  # Example: Replace with actual column names
    'price',
    'asin',
    'amazon_url',
    'cost_price',
    'sale_price',
    'profit',
    'profit_margin',
    'estimated_sales',
    'sales_rank',
    'source_url'
]

try:
    # Connect to the database
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()
    print("Connected to the database!")

    # Open the CSV file
    with open(csv_file, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=',')  # Use ',' if the CSV is comma-delimited
        
        # Insert data into the products table
        for row in reader:
            try:
                # Extract data (allow empty values)
                name = row.get('product_name', '').strip()
                price = float(row['price']) if row.get('price') and row['price'].strip() else None
                asin = row.get('asin', '').strip() or None
                amazon_url = row.get('amazon_url', '').strip() or None
                cost_price = float(row['cost_price']) if row.get('cost_price') and row['cost_price'].strip() else None
                sale_price = float(row['sale_price']) if row.get('sale_price') and row['sale_price'].strip() else None
                profit = float(row['profit']) if row.get('profit') and row['profit'].strip() else None
                profit_margin = float(row['profit_margin']) if row.get('profit_margin') and row['profit_margin'].strip() else None
                estimated_sales = int(row['estimated_sales']) if row.get('estimated_sales') and row['estimated_sales'].strip() else None
                sales_rank = int(row['sales_rank']) if row.get('sales_rank') and row['sales_rank'].strip() else None
                source_url = row.get('source_url', '').strip() or None

                # Skip rows with missing required columns (if needed)
                skip_row = False
                for column in required_columns:
                    value = row.get(column, '').strip()
                    if not value:
                        print(f"Skipping row due to missing or null value in column '{column}': {row}")
                        skip_row = True
                        break

                if skip_row:
                    continue  # Skip this row and move to the next one

                # SQL INSERT statement with parameterized query
                insert_query = """
                    INSERT INTO products (
                        name, price, asin, amazon_url, cost_price, sale_price,
                        profit, profit_margin, estimated_sales, sales_rank, source_url
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                """
                
                # Execute the INSERT statement
                cur.execute(insert_query, (
                    name, price, asin, amazon_url, cost_price, sale_price,
                    profit, profit_margin, estimated_sales, sales_rank, source_url
                ))
                print(f"Inserted: {name}")

            except ValueError as ve:
                print(f"Skipping row due to invalid data: {ve}")
                conn.rollback()  # Roll back the transaction to allow further commands
            except Exception as e:
                print(f"Error inserting row: {e}")
                conn.rollback()  # Roll back the transaction to allow further commands

    # Commit the transaction
    conn.commit()
    print("Data inserted successfully!")

except psycopg2.Error as e:
    print(f"Database error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")

finally:
    # Close the database connection
    if conn:
        cur.close()
        conn.close()
        print("Database connection closed.")
