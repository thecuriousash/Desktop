import sqlite3

conn = sqlite3.connect('hustl.db')
try:
    # Add the missing brand column
    conn.execute('ALTER TABLE market_items ADD COLUMN brand TEXT')
    # Add the missing user_id column
    conn.execute('ALTER TABLE market_items ADD COLUMN user_id INTEGER')
    conn.commit()
    print("Columns added successfully!")
except sqlite3.OperationalError as e:
    print(f"Note: {e} (They might already exist)")
finally:
    conn.close()