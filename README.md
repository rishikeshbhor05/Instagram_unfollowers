# Instagram Unfollowers

🔗 **Live app:** [followers-auditer.onrender.com](https://followers-auditer.onrender.com)

Find out who you follow on Instagram that doesn't follow you back. You can use the hosted version above, or run it locally — either way, nothing is stored: the ZIP you upload is deleted immediately after processing.

> **Note on the free hosting tier:** the live app sleeps after ~15 minutes of no traffic, so the first visit after a quiet period can take 30-60 seconds to wake up. Totally normal, just refresh if it seems stuck.

## How it works

1. You download your Instagram data as a ZIP file (steps below).
2. You upload that ZIP to this app.
3. The app reads your `followers_*.json` and `following.json` files, compares them, and shows you everyone you follow who doesn't follow you back — each with a button that opens their profile so you can unfollow them yourself.

This app never logs into Instagram, never uses your password, and can't unfollow anyone automatically. It just reads the data Instagram already gave you and does the comparison.

## Running it locally (optional — the hosted version above works without any setup)

If you'd rather run it yourself instead of using the hosted link:

### Requirements

- Python 3.8+
- Flask

## Setup

```bash
# Clone the repo
git clone <your-repo-url>
cd <your-repo-folder>

# (Optional but recommended) create a virtual environment
python -m venv venv
source venv/bin/activate      # macOS/Linux
venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

Then open **http://127.0.0.1:5000** in your browser.

### Opening it on your phone (same Wi-Fi network)

The app already binds to `0.0.0.0`, so once it's running:

1. Find your computer's local IP address:
   - Windows: `ipconfig` → look for "IPv4 Address"
   - macOS/Linux: `ifconfig` or `ip addr`
2. On your phone (connected to the same Wi-Fi), visit `http://<your-computer-ip>:5000`

If it doesn't load, check that your computer's firewall isn't blocking port 5000.

## How to download your Instagram data (the ZIP this app needs)

1. Open the Instagram app or go to [instagram.com](https://www.instagram.com) and log in.
2. Go to **Settings and privacy → Accounts Center → Your information and permissions → Download your information**.
3. Choose your Instagram account, then select **"Some of your information."**
4. Under the categories, select **"Followers and following"** (you can deselect everything else to keep the download small and fast).
5. Set the **date range to "All time"** — this matters, a shorter range will give you an incomplete follower list.
6. Choose **format: JSON** (not HTML) — the app only reads JSON.
7. Submit the request. Instagram will email you (or notify you in-app) when the export is ready — this can take anywhere from a few minutes to a day or two depending on account size.
8. Download the ZIP file from the link Instagram provides once it's ready.

## Using the app

1. Run the app (`python app.py`) and open it in your browser.
2. Click **"Choose Instagram ZIP"** and select the ZIP file you downloaded from Instagram.
3. Click **"Check Unfollowers."**
4. You'll see your following/followers counts and a list of everyone who doesn't follow you back. Click **"Unfollow →"** next to any username to open their profile in a new tab and unfollow them manually.

## Deploying your own copy for free

Want to run your own instance instead of using the hosted link? This repo is set up to deploy on [Render](https://render.com)'s free tier — no credit card required.

1. Push this repo to GitHub (see steps above).
2. Go to [render.com](https://render.com) and sign up / log in with GitHub.
3. Click **New +** → **Web Service**, and connect your GitHub repo.
4. Render should auto-detect Python. Set:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app` (already set via the included `Procfile`, so this may auto-fill)
   - **Instance Type:** Free
5. Click **Create Web Service**. Render will build and deploy — you'll get a public URL like `https://your-app-name.onrender.com`.

**Heads up on the free tier:**
- The app spins down after ~15 minutes of no traffic and takes 30-60 seconds to wake up on the next visit. Normal for free hosting — just a one-time delay per visitor after idle periods.
- The filesystem is ephemeral (wiped on redeploy/restart), which is actually fine here since uploaded ZIPs are deleted immediately after processing anyway — nothing needs to persist.
- `FLASK_DEBUG` is off by default, which is required for public deployment — don't set `FLASK_DEBUG=1` in Render's environment variables.

**A note on privacy:** once this is public, anyone using it will be uploading their own personal Instagram export data to your server. The app already deletes uploads immediately after processing, but if you expect real usage, it's worth adding to the README/UI that you don't store their data, and keeping the `MAX_CONTENT_LENGTH` cap in place (already set at 50MB) so nobody can hammer your free instance with huge files.

## Notes

- Uploaded ZIP files are deleted from the server immediately after processing — nothing is stored.
- Usernames are matched case-insensitively.
- Debug mode is **off by default**. For local development only, you can enable it with `FLASK_DEBUG=1 python app.py`. Never enable it on a public deployment — the Flask debugger allows remote code execution if left on and reachable from the internet.
- This project is for personal use. The hosted version runs on Render's free tier with `gunicorn` as the production server.
