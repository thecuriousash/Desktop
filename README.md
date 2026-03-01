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
| `DATABASE_URL` | ✅ | — | PostgreSQL connection string (`postgres://user:pass@host/db`) |
| `SUPABASE_URL` | ✅ | — | Supabase project URL |
| `SUPABASE_KEY` | ✅ | — | Supabase API key (anon) |
| `SECRET_KEY` | ✅ | `hustl_dev_fallback_key` | Flask session secret |
| `ADMIN_USERNAME` | ✅ | `admin` | Admin login username |
| `ADMIN_PASSWORD` | ✅ | `changeme` | Admin login password |
| `MAX_CONTENT_LENGTH` | — | `4194304` (4 MB) | Max upload size |
| `ALLOWED_EXTENSIONS` | — | `png,jpg,jpeg,gif` | Allowed file types |
| `SESSION_COOKIE_SECURE` | — | `False` | Set `True` for HTTPS |
| `SESSION_COOKIE_HTTPONLY` | — | `True` | Set `False` for dev only |
| `SESSION_COOKIE_SAMESITE` | — | `Lax` | CSRF protection (`Strict`, `Lax`, `None`) |

## Deploying to Render

1. Create a **Web Service** on [Render](https://render.com)
2. **Set ALL environment variables** in the Render dashboard (especially `DATABASE_URL`, `SUPABASE_URL`, `SUPABASE_KEY`)
3. Build command: `pip install -r requirements.txt`
4. Start command: (uses `Procfile` automatically)
   ```
   gunicorn app:app --bind 0.0.0.0:$PORT --workers 3
   ```
5. Database tables are created automatically on first run via `init_db()`

## Database & Storage

- **Database:** PostgreSQL (via Supabase) — required for production
- **Storage:** Supabase Storage bucket (`market-images`) for all file uploads
- **Connection Issues on Render?** 
  - Ensure `DATABASE_URL` is set in Render's environment variables
  - Verify the PostgreSQL endpoint is reachable from Render (may require IPv4 enforcement)
  - Check Supabase network rules allow inbound connections
README.md               # This file
├── .env.example            # Environment variable template
├── .gitignore
├── static/
│   ├── style.css           # Styling
│   └── images/             # Fallback images (default.png)
└── templates/
    ├── base.html           # Layout with nav + footer
    ├── auth.html           # Login / Signup combined
    ├── index.html          # Home page
    ├── market.html         # Marketplace listings grid
    ├── list_item.html      # Seller: add new listing (POST handler in /market)
    ├── listing_detail.html # Individual listing page
    ├── seller_dash.html    # Seller dashboard & management
    ├── seller_onboarding.html  # Become a seller form
    ├── seller_profile.html # Public seller profile
    ├── pending_approval.html    # Waiting for admin verification
    ├── lost.html           # Lost & found board
    ├── admin_login.html    # Admin authentication
    ├── admin/
    │   ├── dashboard.html  # Admin verification & claim requests
    │   ├── manage_items.html   # Delete market items
    │   └── users.html      # View all users & their statusesgrid
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
