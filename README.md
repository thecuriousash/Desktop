# HUSTL. | Campus Marketplace Protocol 💎

HUSTL is a high-trust, closed-loop marketplace ecosystem designed for university campuses. It features a dual-protocol entry system for Buyers and Sellers, governed by an administrator verification layer to ensure safety and authenticity in campus trades.

![Hustl Interface](/static/images/default.png)

## 🚀 Live Demo

**URL:** [https://desktop-n3ar.onrender.com](https://desktop-n3ar.onrender.com)

---

## ☁️ How to Redeploy on Render (Step-by-Step)

If you are seeing a `404 Not Found` or the old version of the site on your Render link, it means the latest code hasn't finished deploying yet. Follow these steps to ensure your app deploys the new refactored version perfectly:

### Step 1: Push Latest Code to GitHub
Ensure all your local changes are pushed to your GitHub repository:
```bash
git add .
git commit -m "update"
git push origin main
```

### Step 2: Configure Render Dashboard
1. Log in to your [Render Dashboard](https://dashboard.render.com/).
2. Click on your **Web Service** (e.g., `desktop`).
3. On the left sidebar, click **Environment**.
4. You **MUST** add these three Environment Variables (click "Add Environment Variable"):
   - `SECRET_KEY` = (Type any random string of characters, e.g., `super_secret_hustl_key_2026`)
   - `ADMIN_USERNAME` = `admin` (Or whatever you want your admin username to be)
   - `ADMIN_PASSWORD` = `changeme` (Or a secure password for your admin panel)
5. Click **Save Changes**.

### Step 3: Trigger a Manual Deploy
1. Still on the Render dashboard for your web service, click **Settings** on the left.
2. Scroll down to **Build & Deploy**.
3. Ensure your settings match this:
   - **Repository:** `https://github.com/thecuriousash/Desktop`
   - **Branch:** `main`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT` (Render should auto-detect this via the `Procfile`, but put it here if asked).
4. Scroll to the top right of the page, click the **Manual Deploy** button, and select **Clear build cache & deploy**.

### Step 4: Wait for the Build
Click on the **Logs** tab on the left. You will see text scrolling as Render installs Python and your requirements. 
Wait until you see the green text: **"Your service is live 🎉"**. 

Once you see that, refresh your `desktop-n3ar.onrender.com` link, and the new `/auth/buyer` routes will work perfectly!

---

## 🛠️ System Architecture

The platform is built on a "Vetting-First" logic:
1. **The Vault:** New sellers must submit legal credentials and ID proof.
2. **The Mediator:** Administrators review submissions via a secure oversight dashboard.
3. **The Exchange:** Verified users gain "Direct Entry" to post assets. Buyers can browse and view items securely.

## 💻 Tech Stack
- **Backend:** Python / Flask
- **Database:** SQLite3 (Row Factory Pattern)
- **Frontend:** HTML5 / Tailwind CSS (Glassmorphism UI)
- **Deployment:** Render (Gunicorn)

## 📂 Project Structure
```text
hustl/
├── app.py              # Core Logic & Routing 
├── hustl.db            # SQLite Database (Auto-generated)
├── requirements.txt    # Python dependencies
├── Procfile            # Render web server configuration
├── .env.example        # Environment variable template
├── static/
│   ├── style.css       # Custom styles
│   └── images/         # Uploaded images & default placeholders
└── templates/          # Glassmorphism HTML UI Components
    ├── base.html       # Global Layout
    ├── login.html      # Authentication
    ├── market.html     # The Exchange
    ├── lost.html       # Lost & Found reporting
    ├── index.html      # Mediator Dashboard / Home
    └── ...             # Detail & Dashboard pages
```
