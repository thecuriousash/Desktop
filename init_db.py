import sqlite3

def init_db():
    conn = sqlite3.connect('hustl.db')
    c = conn.cursor()
    
    # Users Table (Section 8)
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY, name TEXT, email TEXT, 
                  reg_number TEXT UNIQUE, role TEXT DEFAULT 'pending')''')
    
    # Products Table (Section 8)
    c.execute('''CREATE TABLE IF NOT EXISTS products 
                 (id INTEGER PRIMARY KEY, title TEXT, price REAL, 
                  whatsapp TEXT, image TEXT, is_sold INTEGER DEFAULT 0)''')
    
    # Lost & Found Table (Section 8)
    c.execute('''CREATE TABLE IF NOT EXISTS lost_found 
                 (id INTEGER PRIMARY KEY, title TEXT, description TEXT, 
                  location TEXT, custody TEXT, is_resolved INTEGER DEFAULT 0)''')
    
    conn.commit()
    conn.close()

init_db()