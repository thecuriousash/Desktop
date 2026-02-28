import sqlite3
import os
from flask import Flask, render_template, request, redirect, session, url_for, flash, abort
from werkzeug.utils import secure_filename
import logging

app = Flask(__name__)
# Load secrets from environment for production readiness
app.secret_key = os.environ.get('SECRET_KEY', 'hustl_dev_fallback_key')

# Production/session security settings (override via env in Render)
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('SESSION_COOKIE_SECURE', 'False') == 'True'
app.config['SESSION_COOKIE_HTTPONLY'] = os.environ.get('SESSION_COOKIE_HTTPONLY', 'True') == 'True'
app.config['SESSION_COOKIE_SAMESITE'] = os.environ.get('SESSION_COOKIE_SAMESITE', 'Lax')

# Upload limits and allowed extensions
app.config['MAX_CONTENT_LENGTH'] = int(os.environ.get('MAX_CONTENT_LENGTH', 4 * 1024 * 1024))  # 4 MB default
ALLOWED_EXTENSIONS = set(os.environ.get('ALLOWED_EXTENSIONS', 'png,jpg,jpeg,gif').split(','))

# Admin credentials from env vars (never hardcode in production)
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'changeme')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- CONFIG ---
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'images')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

DATABASE = os.path.join(app.root_path, 'hustl.db')

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# safe execute helper: wraps execute/commit and logs errors
def safe_execute(conn, sql, params=(), commit=False, fetchone=False, fetchall=False):
    try:
        cur = conn.execute(sql, params)
        if commit:
            conn.commit()
        if fetchone:
            return cur.fetchone()
        if fetchall:
            return cur.fetchall()
        return cur
    except sqlite3.Error:
        logging.exception('DB error executing SQL: %s | params=%s', sql, params)
        return None


def init_db():
    conn = get_db_connection()
    try:
        # Create base tables if they don't exist
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
                        is_sold INTEGER DEFAULT 0,
                        seller_brand TEXT, user_id INTEGER)''')

        conn.execute('''CREATE TABLE IF NOT EXISTS lost_items (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT, description TEXT, location TEXT, custody TEXT,
                        image TEXT)''')

        # Ensure expected columns exist (migration for older DBs)
        cur = conn.execute("PRAGMA table_info('users')")
        users_cols = {row['name'] for row in cur.fetchall()}
        if 'is_verified' not in users_cols:
            conn.execute("ALTER TABLE users ADD COLUMN is_verified INTEGER DEFAULT 0")
        if 'role' not in users_cols:
            conn.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'pending_verification'")

        cur = conn.execute("PRAGMA table_info('market_items')")
        items_cols = {row['name'] for row in cur.fetchall()}
        if 'seller_brand' not in items_cols:
            conn.execute("ALTER TABLE market_items ADD COLUMN seller_brand TEXT")
        if 'user_id' not in items_cols:
            conn.execute("ALTER TABLE market_items ADD COLUMN user_id INTEGER")
        if 'brand' not in items_cols:
            conn.execute("ALTER TABLE market_items ADD COLUMN brand TEXT")

        cur = conn.execute("PRAGMA table_info('lost_items')")
        lost_cols = {row['name'] for row in cur.fetchall()}
        if 'image' not in lost_cols:
            conn.execute("ALTER TABLE lost_items ADD COLUMN image TEXT")

        conn.commit()
    finally:
        conn.close()

init_db()


# --- HELPER: require login ---
def get_current_user():
    """Return the current user row or None."""
    email = session.get('email')
    if not email:
        return None
    conn = get_db_connection()
    try:
        user = safe_execute(conn, 'SELECT * FROM users WHERE email = ?', (email,), fetchone=True)
        return user
    finally:
        conn.close()


# --- ROUTES ---

@app.route("/")
def index():
    pending_users = []
    market_oversight = []
    if session.get('is_admin'):
        conn = get_db_connection()
        try:
            pending_users = safe_execute(
                conn,
                'SELECT * FROM users WHERE is_verified = 0 AND reg_number IS NOT NULL',
                fetchall=True
            ) or []
            market_oversight = safe_execute(
                conn,
                '''SELECT market_items.*, users.display_name AS seller_display
                   FROM market_items
                   LEFT JOIN users ON market_items.user_id = users.id
                   ORDER BY market_items.id DESC''',
                fetchall=True
            ) or []
        finally:
            conn.close()
    return render_template("index.html", pending_users=pending_users, market_oversight=market_oversight)


# --- LOGIN (replaces the hardcoded fake email) ---
@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get('email'):
        return redirect(url_for('market_choice'))
    if request.method == "POST":
        email = (request.form.get('email') or '').strip().lower()
        if not email or '@' not in email:
            flash("Please enter a valid email address.", "error")
            return render_template("login.html")
        session['email'] = email
        # Create user record if it doesn't exist
        conn = get_db_connection()
        try:
            existing = safe_execute(conn, 'SELECT id FROM users WHERE email = ?', (email,), fetchone=True)
            if not existing:
                safe_execute(conn, 'INSERT INTO users (email) VALUES (?)', (email,), commit=True)
        finally:
            conn.close()
        return redirect(url_for('market_choice'))
    return render_template("login.html")


@app.route("/market-choice")
def market_choice():
    if not session.get('email'):
        return redirect(url_for('login'))
    return render_template("market_choice.html")


@app.route("/enter-protocol/<u_type>")
def enter_protocol(u_type):
    if not session.get('email'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    try:
        user = safe_execute(conn, 'SELECT * FROM users WHERE email = ?', (session['email'],), fetchone=True)

        if not user:
            safe_execute(conn, 'INSERT INTO users (email, user_type) VALUES (?, ?)',
                         (session['email'], u_type), commit=True)
            return redirect(url_for('verification_vault'))

        safe_execute(conn, 'UPDATE users SET user_type = ? WHERE email = ?',
                     (u_type, session['email']), commit=True)
        # re-fetch user after update to read latest fields
        user = safe_execute(conn, 'SELECT * FROM users WHERE email = ?', (session['email'],), fetchone=True)
    finally:
        conn.close()

    if user and user['is_verified'] == 1:
        if u_type == 'seller':
            return redirect(url_for('seller_dash'))
        return redirect(url_for('market'))

    if user and user['reg_number']:
        return render_template("pending_approval.html")

    return redirect(url_for('verification_vault'))


# compatibility route used by templates that expect `/auth/<role>`
@app.route("/auth/<u_type>")
def auth(u_type):
    return redirect(url_for('enter_protocol', u_type=u_type))


@app.route("/verification-vault")
def verification_vault():
    if not session.get('email'):
        return redirect(url_for('login'))
    conn = get_db_connection()
    try:
        user = safe_execute(conn, 'SELECT * FROM users WHERE email = ?', (session['email'],), fetchone=True)
    finally:
        conn.close()
    return render_template("verification_vault.html", user_type=(user['user_type'] if user else 'seller'))


@app.route("/submit-vault", methods=["POST"])
def submit_vault():
    if not session.get('email'):
        return redirect("/")
    legal_name = request.form.get('legal_name')
    display_name = request.form.get('display_name')
    reg_number = request.form.get('reg_number')
    whatsapp = request.form.get('whatsapp')
    id_proof_link = request.form.get('id_proof_link')
    social_link = request.form.get('social_link')

    conn = get_db_connection()
    try:
        safe_execute(conn, '''UPDATE users SET legal_name=?, display_name=?, reg_number=?, whatsapp=?,
                        id_proof_link=?, social_link=?, role='pending_verification', is_verified=0
                        WHERE email = ?''',
                     (legal_name, display_name, reg_number, whatsapp, id_proof_link,
                      social_link, session['email']), commit=True)
    finally:
        conn.close()
    return render_template("pending_approval.html")


@app.route("/market", methods=["GET", "POST"])
def market():
    if not session.get('email'):
        return redirect(url_for('login'))
    conn = get_db_connection()
    try:
        user = safe_execute(conn, 'SELECT * FROM users WHERE email = ?', (session['email'],), fetchone=True)

        if request.method == "POST":
            # Only verified sellers can post
            if not user or user['is_verified'] != 1 or user['user_type'] != 'seller':
                flash("Only verified sellers can post items.", "error")
                return redirect(url_for('market'))

            img = request.files.get("image")
            filename = 'default.png'
            if img and img.filename:
                if not allowed_file(img.filename):
                    flash("File type not allowed.", "error")
                    return redirect(url_for('market'))
                filename = secure_filename(img.filename)
                img.save(os.path.join(UPLOAD_FOLDER, filename))

            brand = request.form.get('brand') or (user['display_name'] if user else None)
            seller_brand = user['display_name'] if user else None
            user_id = user['id'] if user else None

            safe_execute(conn, '''INSERT INTO market_items (title, brand, price, whatsapp, image, seller_brand, user_id)
                            VALUES (?,?,?,?,?,?,?)''',
                         (request.form.get('title'), brand, request.form.get('price'),
                          request.form.get('whatsapp'), filename, seller_brand, user_id), commit=True)
            return redirect(url_for('market'))

        items = safe_execute(conn, '''SELECT market_items.*, users.display_name AS seller_display
                                FROM market_items
                                LEFT JOIN users ON market_items.user_id = users.id
                                WHERE market_items.is_sold = 0
                                ORDER BY market_items.id DESC''', fetchall=True) or []
    finally:
        conn.close()
    return render_template("market.html", items=items,
                           user_type=(user['user_type'] if user else 'buyer'),
                           user=user)


# --- LIST ITEM (dedicated seller page) ---
@app.route("/list-item")
def list_item():
    if not session.get('email'):
        return redirect(url_for('login'))
    user = get_current_user()
    if not user or user['is_verified'] != 1 or user['user_type'] != 'seller':
        flash("Only verified sellers can list items.", "error")
        return redirect(url_for('market'))
    return render_template("list_item.html")


# --- LISTING DETAIL ---
@app.route("/listing/<int:item_id>")
def listing_detail(item_id):
    conn = get_db_connection()
    try:
        item = safe_execute(conn, 'SELECT * FROM market_items WHERE id = ?', (item_id,), fetchone=True)
        if not item:
            abort(404)
        other_products = []
        if item['user_id']:
            other_products = safe_execute(
                conn,
                'SELECT * FROM market_items WHERE user_id = ? AND id != ? AND is_sold = 0 ORDER BY id DESC',
                (item['user_id'], item_id), fetchall=True
            ) or []
    finally:
        conn.close()
    return render_template("listing_detail.html", item=item, other_products=other_products, quantity=1)


# --- SELLER DASHBOARD ---
@app.route("/seller-dash")
def seller_dash():
    if not session.get('email'):
        return redirect(url_for('login'))
    conn = get_db_connection()
    try:
        user = safe_execute(conn, 'SELECT * FROM users WHERE email = ?', (session['email'],), fetchone=True)
        if not user or user['user_type'] != 'seller':
            return redirect(url_for('market'))
        items = safe_execute(
            conn,
            'SELECT * FROM market_items WHERE user_id = ? ORDER BY id DESC',
            (user['id'],), fetchall=True
        ) or []
    finally:
        conn.close()
    return render_template("seller_dash.html", items=items, user=user)


# --- SELLER PROFILE (public) ---
@app.route("/seller/<int:user_id>")
def seller_profile(user_id):
    conn = get_db_connection()
    try:
        seller = safe_execute(conn, 'SELECT * FROM users WHERE id = ? AND is_verified = 1',
                              (user_id,), fetchone=True)
        if not seller:
            abort(404)
        items = safe_execute(
            conn,
            'SELECT * FROM market_items WHERE user_id = ? AND is_sold = 0 ORDER BY id DESC',
            (user_id,), fetchall=True
        ) or []
    finally:
        conn.close()
    return render_template("seller_profile.html",
                           name=seller['display_name'],
                           whatsapp=seller['whatsapp'],
                           items=items,
                           join_date="2026")


# --- MARK SOLD ---
@app.route("/market/sold/<int:item_id>")
def mark_sold(item_id):
    if not session.get('email'):
        return redirect(url_for('login'))
    conn = get_db_connection()
    try:
        user = safe_execute(conn, 'SELECT * FROM users WHERE email = ?', (session['email'],), fetchone=True)
        item = safe_execute(conn, 'SELECT * FROM market_items WHERE id = ?', (item_id,), fetchone=True)
        if not user or not item:
            abort(404)
        # Only the seller who owns the item (or admin) can mark it sold
        if item['user_id'] != user['id'] and not session.get('is_admin'):
            abort(403)
        safe_execute(conn, 'UPDATE market_items SET is_sold = 1 WHERE id = ?', (item_id,), commit=True)
    finally:
        conn.close()
    return redirect(url_for('seller_dash'))


# --- LOST AND FOUND ---
@app.route("/lost", methods=["GET", "POST"])
def lost():
    conn = get_db_connection()
    try:
        if request.method == "POST":
            img = request.files.get("image")
            filename = None
            if img and img.filename and img.filename != '':
                if not allowed_file(img.filename):
                    flash("File type not allowed.", "error")
                    return redirect(url_for('lost'))
                filename = secure_filename(img.filename)
                img.save(os.path.join(UPLOAD_FOLDER, filename))

            title = request.form.get('title', 'Unknown Item')
            description = request.form.get('description', 'No description provided.')
            location = request.form.get('location', 'Unknown Location')
            custody = request.form.get('custody', 'With Mediator')

            safe_execute(conn,
                         'INSERT INTO lost_items (title, description, location, custody, image) VALUES (?,?,?,?,?)',
                         (title, description, location, custody, filename), commit=True)
            return redirect(url_for('lost'))

        items = safe_execute(conn, 'SELECT * FROM lost_items ORDER BY id DESC', fetchall=True) or []
    finally:
        conn.close()
    return render_template("lost.html", items=items)


# --- ADMIN ROUTES ---

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if (request.form.get("username") == ADMIN_USERNAME and
                request.form.get("password") == ADMIN_PASSWORD):
            session['is_admin'] = True
            return redirect(url_for('index'))
        flash("Invalid credentials.", "error")
    return render_template("admin_login.html")


@app.route("/admin/verify/<int:uid>")
def verify_user(uid):
    if not session.get('is_admin'):
        return redirect("/")
    conn = get_db_connection()
    try:
        safe_execute(conn, 'UPDATE users SET is_verified = 1 WHERE id = ?', (uid,), commit=True)
    finally:
        conn.close()
    return redirect(url_for('index'))


@app.route("/admin/manage-items")
def admin_manage_items():
    if not session.get('is_admin'):
        return redirect("/")
    conn = get_db_connection()
    try:
        items = safe_execute(conn, '''SELECT market_items.*, users.legal_name AS legal_name,
                                 users.display_name AS user_display
                                 FROM market_items LEFT JOIN users ON market_items.user_id = users.id
                                 ORDER BY market_items.id DESC''', fetchall=True) or []
    finally:
        conn.close()
    return render_template("admin_items.html", items=items)


@app.route("/admin/delete-item/<int:item_id>")
def admin_delete_item(item_id):
    if not session.get('is_admin'):
        return redirect("/")
    conn = get_db_connection()
    try:
        # Optionally delete the image file
        item = safe_execute(conn, 'SELECT image FROM market_items WHERE id = ?', (item_id,), fetchone=True)
        if item and item['image'] and item['image'] != 'default.png':
            img_path = os.path.join(UPLOAD_FOLDER, item['image'])
            if os.path.exists(img_path):
                os.remove(img_path)
        safe_execute(conn, 'DELETE FROM market_items WHERE id = ?', (item_id,), commit=True)
    finally:
        conn.close()
    # Redirect back to wherever the admin came from
    return redirect(request.referrer or url_for('admin_manage_items'))


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)