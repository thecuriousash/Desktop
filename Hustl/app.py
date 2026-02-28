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
                    role TEXT DEFAULT 'pending_verification')''')
    
    conn.execute('''CREATE TABLE IF NOT EXISTS market_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    title TEXT, price TEXT, whatsapp TEXT, image TEXT, 
                    is_sold INTEGER DEFAULT 0, seller_brand TEXT)''')
    
    conn.execute('''CREATE TABLE IF NOT EXISTS lost_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    title TEXT, description TEXT, location TEXT, custody TEXT, image TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- 1. THE HOMEPAGE & MARKET CHOICE ---

@app.route("/")
def index():
    pending_users = []
    market_oversight = []
    if session.get('is_admin'):
        conn = get_db_connection()
        pending_users = conn.execute('SELECT * FROM users WHERE role = "pending_verification" AND reg_number IS NOT NULL').fetchall()
        market_oversight = conn.execute('SELECT * FROM market_items').fetchall()
        conn.close()
    return render_template("index.html", pending_users=pending_users, market_oversight=market_oversight)

@app.route("/market-choice")
def market_choice():
    # This matches the button link <a href="/market-choice">
    return render_template("market_choice.html")

# --- 2. ADMIN & MEDIATOR LOGIC ---

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        # Get data from the form
        user = request.form.get("username")
        pw = request.form.get("password")
        
        # CHANGE THESE STRINGS TO YOUR PREFERRED LOGIN
        if user == "silfira" and pw == "ashlinu":
            session['is_admin'] = True
            return redirect(url_for('index'))
        
        return "Unauthorized", 401
    return render_template("admin_login.html")

@app.route("/admin/verify/<int:uid>")
def verify_user(uid):
    if not session.get('is_admin'): return redirect("/")
    conn = get_db_connection()
    conn.execute('UPDATE users SET role = "verified_user" WHERE id = ?', (uid,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route("/admin/delete-item/<int:iid>")
def delete_item(iid):
    if not session.get('is_admin'): return redirect("/")
    conn = get_db_connection()
    conn.execute('DELETE FROM market_items WHERE id = ?', (iid,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# --- 3. USER AUTH FLOW ---

@app.route("/auth/<u_type>")
def auth_trigger(u_type):
    session['user_type'] = u_type
    session['email'] = "demo@college.edu" 
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (session['email'],)).fetchone()
    if not user:
        conn.execute('INSERT INTO users (email, user_type) VALUES (?, ?)', (session['email'], u_type))
        conn.commit()
    conn.close()
    return redirect(url_for('verification_vault'))

@app.route("/verification-vault")
def verification_vault():
    if not session.get('email'): return redirect("/")
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (session['email'],)).fetchone()
    conn.close()
    session['user_role'] = user['role']
    if user['role'] == 'verified_user':
        # If verified, buyers go to market, sellers go to dashboard (studio)
        return redirect(url_for('market') if user['user_type'] == 'buyer' else url_for('dashboard'))
    return render_template("verification_vault.html", user_type=session.get('user_type'))

@app.route("/submit-vault", methods=["POST"])
def submit_vault():
    conn = get_db_connection()
    conn.execute('''UPDATE users SET legal_name = ?, display_name = ?, reg_number = ?, 
                    whatsapp = ?, id_proof_link = ?, social_link = ? WHERE email = ?''', 
                 (request.form['legal_name'], request.form['display_name'], request.form['reg_number'], 
                  request.form['whatsapp'], request.form['id_proof_link'], request.form['social_link'], session['email']))
    conn.commit()
    conn.close()
    # Ensure you have a 'pending_screen.html' template
    return render_template("pending_screen.html")

# --- 4. MARKET, LOST, & STUDIO ---

@app.route("/market")
def market():
    if not session.get('email'): return redirect("/")
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM market_items ORDER BY id DESC').fetchall()
    conn.close()
    return render_template("market.html", items=items)

@app.route("/lost", methods=["GET", "POST"])
def lost():
    conn = get_db_connection()
    if request.method == "POST":
        img = request.files.get("image")
        filename = secure_filename(img.filename) if img and img.filename != '' else None
        if filename: img.save(os.path.join(UPLOAD_FOLDER, filename))
        conn.execute('INSERT INTO lost_items (title, description, location, custody, image) VALUES (?,?,?,?,?)',
                     (request.form['title'], request.form['description'], request.form['location'], request.form['custody'], filename))
        conn.commit()
        return redirect(url_for('lost'))
    items = conn.execute('SELECT * FROM lost_items ORDER BY id DESC').fetchall()
    conn.close()
    return render_template("lost.html", items=items)

@app.route("/dashboard")
def dashboard():
    # This is the "Studio" page for sellers
    if not session.get('email'): return redirect("/")
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (session['email'],)).fetchone()
    items = conn.execute('SELECT * FROM market_items WHERE seller_brand = ?', (user['display_name'],)).fetchall()
    conn.close()
    return render_template("seller_dash.html", items=items)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True, port=50000)