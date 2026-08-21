# Instagram Unfollowers

Find out who you follow on Instagram that doesn't follow you back — all processed locally on your own machine. Nothing is uploaded anywhere except to your own Flask server, and the ZIP you upload is deleted immediately after processing.

## How it works

1. You download your Instagram data as a ZIP file (steps below).
2. You upload that ZIP to this app.
3. The app reads your `followers_*.json` and `following.json` files, compares them, and shows you everyone you follow who doesn't follow you back — each with a button that opens their profile so you can unfollow them yourself.
4. While downloading the file from instagram make sure you check only the Followers and following section to be downloaded. Also for the duration or time period, select all time nothing else.

This app never logs into Instagram, never uses your password, and can't unfollow anyone automatically. It just reads the data Instagram already gave you and does the comparison.

## Requirements

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

## Notes

- Uploaded ZIP files are deleted from the server immediately after processing — nothing is stored.
- Usernames are matched case-insensitively.
- `debug=True` is set in `app.py` for local development convenience. Turn this off (`debug=False`) before deploying anywhere beyond your own machine — the Flask debugger allows remote code execution if left on in a reachable environment.
- This project is for personal, local use. It is not intended to be deployed as a public-facing web service without further hardening (rate limiting, HTTPS, etc.).
