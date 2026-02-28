import sqlite3

conn = sqlite3.connect('hustl.db')
try:
    # This adds the missing link between the product and the seller
    conn.execute('ALTER TABLE market_items ADD COLUMN user_id INTEGER')
    conn.commit()
    print("Column user_id added successfully!")
except sqlite3.OperationalError:
    print("Column already exists or table not found.")
conn.close()