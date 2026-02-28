# Hustl. — Campus Mini-Economy

A Flask-based campus marketplace for students to **buy/sell items** and report **lost & found** assets, with admin-mediated identity verification.

## Features

- **Buyer / Seller roles** with identity verification
- **Market Exchange** — list, browse, and contact sellers via WhatsApp
- **Lost & Found** — report and track missing items
- **Admin Panel** — verify student IDs, manage listings, delete items
- **Seller Dashboard** — manage your own listings, mark items as sold

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python3 app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000)

**Default admin login:** `admin` / `changeme` (change via env vars in production!)

## Environment Variables

Copy `.env.example` to `.env` and configure:

| Variable | Required | Default | Description |
|---|---|---|---|
| `SECRET_KEY` | ✅ | `hustl_dev_fallback_key` | Flask session secret |
| `ADMIN_USERNAME` | ✅ | `admin` | Admin login username |
| `ADMIN_PASSWORD` | ✅ | `changeme` | Admin login password |
| `MAX_CONTENT_LENGTH` | — | `4194304` (4 MB) | Max upload size |
| `ALLOWED_EXTENSIONS` | — | `png,jpg,jpeg,gif` | Allowed file types |
| `SESSION_COOKIE_SECURE` | — | `False` | Set `True` for HTTPS |

## Deploying to Render

1. Create a **Web Service** on [Render](https://render.com)
2. Set the environment variables above in the Render dashboard
3. Build command: `pip install -r requirements.txt`
4. Start command: (uses `Procfile` automatically)
   ```
   gunicorn app:app --bind 0.0.0.0:$PORT --workers 3
   ```

> **Note:** SQLite works for small-scale use. For production scale, migrate to PostgreSQL. Uploads are stored locally — use S3/Cloudflare R2 for persistence on ephemeral hosting.

## Project Structure

```
hustl/
├── app.py                  # Flask backend — all routes and DB logic
├── requirements.txt        # Python dependencies
├── Procfile                # Gunicorn config for Render/Heroku
├── .env.example            # Environment variable template
├── .gitignore
├── static/
│   ├── style.css
│   └── images/             # User uploads + default.png
└── templates/
    ├── base.html           # Layout with nav + footer
    ├── login.html          # Email login
    ├── index.html          # Home + admin oversight panel
    ├── market_choice.html  # Buyer / Seller / Lost & Found picker
    ├── verification_vault.html  # Identity verification form
    ├── pending_approval.html    # Waiting for admin approval
    ├── market.html         # Marketplace listings grid
    ├── list_item.html      # Seller: add new listing
    ├── listing_detail.html # Individual listing page
    ├── seller_dash.html    # Seller dashboard
    ├── seller_profile.html # Public seller profile
    ├── lost.html           # Lost & found board
    ├── admin_login.html    # Admin login
    ├── admin.html          # Admin verification table
    └── admin_items.html    # Admin item management
```

## License

MIT
