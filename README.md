# HUSTL. | Campus Marketplace Protocol 💎

HUSTL is a high-trust, closed-loop marketplace ecosystem designed for university campuses. It features a dual-protocol entry system for Buyers and Sellers, governed by a "Mediator" verification layer to ensure safety and authenticity in campus trades.



## 🚀 Live Demo
**URL:** [INSERT_YOUR_DEPLOYED_URL_HERE]

## 🛠️ System Architecture
The platform is built on a "Vetting-First" logic:
1. **The Vault:** New users must submit legal credentials and ID proof.
2. **The Mediator:** Administrators review submissions via a secure oversight dashboard.
3. **The Exchange:** Verified users gain "Direct Entry" to post and browse assets.



## 💻 Tech Stack
- **Backend:** Python / Flask
- **Database:** SQLite3 (Row Factory Pattern)
- **Frontend:** HTML5 / Tailwind CSS (Glassmorphism UI)
- **Deployment:** [Insert Render/PythonAnywhere]

## 📂 Project Structure
```text
Hustl/
├── app.py              # Core Logic & Gatekeeper
├── hustl.db            # SQLite Database
├── static/
│   └── images/         # Asset Storage
└── templates/          # Glassmorphism UI Components
    ├── base.html       # Global Layout
    ├── market.html     # The Exchange
    └── index.html      # Mediator Dashboard
