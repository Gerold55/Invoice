import os
import sys
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import webbrowser
from threading import Timer

from flask import Flask, render_template, request, redirect, url_for, session, jsonify

# --- PATH CONFIGURATION (Supports PyInstaller .exe & standard Python) ---
if getattr(sys, 'frozen', False):
    # If running as a PyInstaller compiled .exe
    BASE_DIR = sys._MEIPASS
else:
    # If running normally via python main.py
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_PATH = os.path.join(BASE_DIR, "safari_config.json")

# Initialize Flask and serve static files from the base directory (for logo.png & manifest.json)
app = Flask(__name__, static_folder=BASE_DIR, static_url_path="")
app.secret_key = "turningskiessafaris_secure_secret_key"  # Encrypts user login session

# --- CONFIGURATION ---
ADMIN_USER = "admin"
ADMIN_PASS = "safari2026"
MANAGER_PIN = "1234"  # PIN required for adding custom unlisted line items
COMPANY_EMAIL = "bookings@turningskiessafaris.com"  # Change to your company's email address

# SMTP Configuration (Example using Gmail App Password)
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "your_email@gmail.com"
SMTP_PASS = "your_email_app_password"

# --- JSON CONFIGURATION LOADER ---
def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"company": {}, "prices": {}, "addons": {}}

@app.route("/", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == ADMIN_USER and password == ADMIN_PASS:
            session["logged_in"] = True
            return redirect(url_for("dashboard"))
        else:
            error = "Invalid username or password."
    return render_template("login.html", error=error)

@app.route("/dashboard")
def dashboard():
    # SECURITY GATE: Prevents viewing index.html without logging in first
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("index.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# --- EXPLICIT MANIFEST ROUTE FOR PWABUILDER ---
@app.route('/manifest.json')
def serve_manifest():
    return app.send_static_file('manifest.json')

@app.route("/api/config", methods=["GET"])
def get_config():
    if not session.get("logged_in"):
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    
    config = load_config()
    comp = config.get("company", {})
    
    # Explicitly return company data including TIN and VRN alongside pricing and add-ons
    return jsonify({
        "success": True, 
        "config": {
            "company": {
                "name": comp.get("name", "Turning Skies Safaris Limited"),
                "info": comp.get("info", ""),
                "tin": comp.get("tin", "203344414"),
                "vrn": comp.get("vrn", "40-330954-B"),
                "payment": comp.get("payment", "")
            },
            "prices": config.get("prices", {}),
            "addons": config.get("addons", {})
        }
    })

@app.route("/api/verify-pin", methods=["POST"])
def verify_pin():
    if not session.get("logged_in"):
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    
    try:
        data = request.json or {}
        entered_pin = data.get("pin", "")
        
        # Verify against Manager PIN or Admin Password
        if entered_pin == MANAGER_PIN or entered_pin == ADMIN_PASS:
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Invalid PIN"}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/send-email", methods=["POST"])
def send_email():
    if not session.get("logged_in"):
        return jsonify({"success": False, "error": "Unauthorized session."}), 401
    
    try:
        data = request.json or {}
        inv_no = data.get("invNo", "INV-0001")
        co_name = data.get("coName", "Turning Skies Safaris Limited")
        client = data.get("client", "Client")
        
        # Build email message
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = COMPANY_EMAIL
        msg['Subject'] = f"New Invoice Generated: {inv_no} - {co_name}"
        
        body = f"""
        A new tax invoice has been generated through the portal.
        
        Invoice Number: {inv_no}
        Client:
        {client}
        
        Please log in to the management system to review full details.
        """
        msg.attach(MIMEText(body, 'plain'))

        # Connect to SMTP server and send
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, COMPANY_EMAIL, msg.as_string())
        server.quit()

        return jsonify({"success": True, "message": "Emailed to company successfully!"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

def open_browser():
    webbrowser.open("http://127.0.0.1:5000/")

if __name__ == "__main__":
    # Opens browser automatically when running locally
    Timer(1, open_browser).start()
    app.run(host="0.0.0.0", port=5000, debug=False)
