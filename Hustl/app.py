import sqlite3
import os
from flask import Flask, render_template, request, redirect, session, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "hustl_final_integrated_2026"

# --- CONFIG ---
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'images')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def get_db_connection():
    conn = sqlite3.connect('hustl.db')
    conn.row_factory = sqlite3.Row 
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    email TEXT UNIQUE, reg_number TEXT, whatsapp TEXT, 
                    display_name TEXT, legal_name TEXT, user_type TEXT, 
                    id_proof_link TEXT, social_link TEXT, 
                    role TEXT DEFAULT 'pending_verification',
                    is_verified INTEGER DEFAULT 0)''')
    
    conn.execute('''CREATE TABLE IF NOT EXISTS market_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    title TEXT, brand TEXT, price TEXT, whatsapp TEXT, image TEXT, 
                    is_sold INTEGER DEFAULT 0, seller_brand TEXT, user_id INTEGER)''')
    
    conn.execute('''CREATE TABLE IF NOT EXISTS lost_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    title TEXT, description TEXT, location TEXT, custody TEXT, image TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- ROUTES ---

@app.route("/")
def index():
    pending_users = []
    if session.get('is_admin'):
        conn = get_db_connection()
        pending_users = conn.execute('SELECT * FROM users WHERE is_verified = 0 AND reg_number IS NOT NULL').fetchall()
        conn.close()
    return render_template("index.html", pending_users=pending_users)

@app.route("/market-choice")
def market_choice():
    return render_template("market_choice.html")

@app.route("/enter-protocol/<u_type>")
def enter_protocol(u_type):
    if not session.get('email'):
        session['email'] = "student@campus.edu"
        
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (session['email'],)).fetchone()
    
    if not user:
        conn.execute('INSERT INTO users (email, user_type) VALUES (?, ?)', (session['email'], u_type))
        conn.commit()
        return redirect(url_for('verification_vault'))
    
    conn.execute('UPDATE users SET user_type = ? WHERE email = ?', (u_type, session['email']))
    conn.commit()
    
    if user['is_verified'] == 1:
        return redirect(url_for('market'))
            
    if user['reg_number']:
        return render_template("pending_approval.html")
        
    return redirect(url_for('verification_vault'))

@app.route("/market", methods=["GET", "POST"])
def market():
    if not session.get('email'): return redirect("/")
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (session['email'],)).fetchone()

    if request.method == "POST":
        img = request.files.get("images")
        filename = secure_filename(img.filename) if img and img.filename != '' else 'default.png'
        if filename != 'default.png':
            img.save(os.path.join(UPLOAD_FOLDER, filename))
            
        conn.execute('''INSERT INTO market_items (title, brand, price, whatsapp, image, seller_brand, user_id) 
                        VALUES (?,?,?,?,?,?,?)''',
                     (request.form.get('title'), request.form.get('brand'), request.form.get('price'), 
                      request.form.get('whatsapp'), filename, user['display_name'], user['id']))
        conn.commit()
        return redirect(url_for('market'))

    items = conn.execute('''SELECT market_items.*, users.display_name FROM market_items 
                            JOIN users ON market_items.user_id = users.id ORDER BY market_items.id DESC''').fetchall()
    conn.close()
    return render_template("market.html", items=items, user_type=user['user_type'])

# --- LOST AND FOUND FIX ---
@app.route("/lost", methods=["GET", "POST"])
def lost():
    conn = get_db_connection()
    if request.method == "POST":
        img = request.files.get("image")
        filename = secure_filename(img.filename) if img and img.filename != '' else None
        if filename:
            img.save(os.path.join(UPLOAD_FOLDER, filename))
        
        # Using .get() prevents KeyError if a field is missing
        title = request.form.get('title', 'Unknown Item')
        description = request.form.get('description', 'No description provided.')
        location = request.form.get('location', 'Unknown Location')
        custody = request.form.get('custody', 'With Mediator')

        conn.execute('INSERT INTO lost_items (title, description, location, custody, image) VALUES (?,?,?,?,?)',
                     (title, description, location, custody, filename))
        conn.commit()
        return redirect(url_for('lost'))
        
    items = conn.execute('SELECT * FROM lost_items ORDER BY id DESC').fetchall()
    conn.close()
    return render_template("lost.html", items=items)

# --- OTHER UTILITIES ---

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form.get("username") == "silfira" and request.form.get("password") == "ashlinu":
            session['is_admin'] = True
            return redirect(url_for('index'))
    return render_template("admin_login.html")

@app.route("/admin/verify/<int:uid>")
def verify_user(uid):
    if not session.get('is_admin'): return redirect("/")
    conn = get_db_connection()
    conn.execute('UPDATE users SET is_verified = 1 WHERE id = ?', (uid,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)