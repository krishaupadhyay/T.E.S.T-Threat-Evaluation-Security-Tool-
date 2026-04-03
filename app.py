"""
Phishing Detection API — Flask Backend

"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import re
import string
import numpy as np
import pandas as pd
from scipy.sparse import hstack

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)


# ─────────────────────────────────────────────
# Load trained components
# ─────────────────────────────────────────────

model      = pickle.load(open("phishing_model.pkl", "rb"))
vectorizer = pickle.load(open("vectorizer.pkl",     "rb"))
scaler     = pickle.load(open("scaler.pkl",         "rb"))


# ─────────────────────────────────────────────
# Text Cleaning
# ─────────────────────────────────────────────

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r"http\S+",  " URLTOKEN ",   text)
    text = re.sub(r"\S+@\S+",  " EMAILTOKEN ", text)
    text = re.sub(r"\d+",      " ",            text)
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = re.sub(r"\s+", " ", text).strip()
    return text


# ─────────────────────────────────────────────
# Feature Engineering
# ─────────────────────────────────────────────

def extract_features(text):
    return pd.DataFrame([[
        int("http" in text or "www" in text),
        int("@" in text),
        int("urgent" in text.lower()),
        text.count("!"),
        len(text)
    ]], columns=["has_link", "has_email", "urgent", "exclamations", "length"])


# ─────────────────────────────────────────────
# URL Extractor
# ─────────────────────────────────────────────

def extract_urls(text):
    return re.findall(r'https?://[^\s]+', text)


# ─────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────

@app.route("/")
def home():
    return "Phishing Detection API Running"


@app.route("/predict", methods=["OPTIONS"])
def predict_options():
    response = jsonify({"status": "ok"})
    response.headers["Access-Control-Allow-Origin"]  = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


@app.route("/predict", methods=["POST"])
def predict():
    flags = []

    # Parse request — JSON only (FormData removed since OCR is gone)
    if request.content_type and request.content_type.startswith("application/json"):
        data       = request.get_json()
        email_text = data.get("email", "")
        deep_scan  = data.get("deep_scan", False)
    else:
        # Fallback: still accept form data (without image)
        email_text = request.form.get("email", "")
        deep_scan  = request.form.get("deep_scan") in [True, "true", "True"]

    if not email_text.strip():
        return jsonify({"error": "No email content provided"}), 400

    # ─────────────────────────────────────────
    # Deep Header Scan
    # ─────────────────────────────────────────

    if deep_scan:
        lower = email_text.lower()
        if "spf=fail"    in lower: flags.append("SPF authentication failed")
        if "dkim=fail"   in lower: flags.append("DKIM verification failed")
        if "received:"   in lower: flags.append("Header routing info detected")
        if "return-path" in lower: flags.append("Return-path header detected")
        if "x-mailer"    in lower: flags.append("X-Mailer header found")

    # ─────────────────────────────────────────
    # ML Prediction
    # ─────────────────────────────────────────

    cleaned      = clean_text(email_text)
    text_vec     = vectorizer.transform([cleaned])
    extra        = extract_features(email_text)
    extra_scaled = scaler.transform(extra)
    final_input  = hstack([text_vec, extra_scaled])

    prediction = model.predict(final_input)[0]
    proba      = model.predict_proba(final_input)[0]
    result     = "Phishing" if prediction == 1 else "Legitimate"

    # ─────────────────────────────────────────
    # FIX: Cap confidence at 95%
    #
    # No real-world classifier can be 100% certain.
    # Raw probability on synthetic data hits 99–100% because
    # the training phrases repeat exactly.
    # We cap at 95% to be honest about model uncertainty.
    # ─────────────────────────────────────────
    raw_confidence = float(proba[1]) * 100
    confidence     = round(min(raw_confidence, 95.0), 2)

    # ─────────────────────────────────────────
    # Rule-based Smart Flags
    # ─────────────────────────────────────────

    lower_email = email_text.lower()

    urgency_words = ["urgent", "immediately", "within", "asap",
                     "suspended", "act now", "expire", "verify now"]
    found = [w for w in urgency_words if w in lower_email]
    if found:
        flags.append(f"Urgency language detected: {', '.join(found)}")

    urls = extract_urls(email_text)
    if urls:
        flags.append(f"{len(urls)} link(s) detected in email")

    for url in urls:
        if any(k in url.lower() for k in ["login", "verify", "secure", "account", "reset", "billing"]):
            flags.append(f"Suspicious URL keyword: {url}")

    impersonation = {
        "paypaI": "PayPal", "paypa1": "PayPal",
        "g00gle": "Google", "arnazon": "Amazon",
        "micros0ft": "Microsoft", "app1e": "Apple"
    }
    for fake, real in impersonation.items():
        if fake.lower() in lower_email:
            flags.append(f"Brand impersonation: '{fake}' pretending to be {real}")

    for url in urls:
        if any(t in url for t in [".xyz", ".tk", ".ml", ".cf", ".top", ".club"]):
            flags.append(f"Suspicious domain TLD: {url}")

    if email_text.count("!") > 3:
        flags.append(f"Excessive exclamation marks ({email_text.count('!')} found)")

    for g in ["dear customer", "dear user", "valued member", "dear account holder"]:
        if g in lower_email:
            flags.append(f"Generic greeting used: '{g}'")

    if "@" in email_text and "http" in email_text:
        flags.append("Email contains both an address and a URL — common in phishing")

    # Remove duplicates, preserve order
    flags = list(dict.fromkeys(flags))

    # ─────────────────────────────────────────
    # Risk Level
    # ─────────────────────────────────────────

    if confidence >= 75:
        risk_level = "HIGH RISK"
    elif confidence >= 40:
        risk_level = "MEDIUM RISK"
    else:
        risk_level = "LOW RISK"

    # ─────────────────────────────────────────
    # Explanation
    # ─────────────────────────────────────────

    if result == "Phishing":
        explanation = (
            f"Phishing detected with {confidence}% confidence. "
            f"Key signals: {', '.join(flags[:3]) if flags else 'suspicious patterns found'}. "
            "Do not click any links or share personal information."
        )
    else:
        explanation = (
            f"Email appears legitimate (phishing probability: {confidence}%). "
            "No strong phishing indicators found. Always remain cautious."
        )

    response = jsonify({
        "result":      result,
        "confidence":  confidence,
        "risk_level":  risk_level,
        "flags":       flags,
        "explanation": explanation,
        "flag_count":  len(flags)
    })
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


if __name__ == "__main__":
    
    app.run(debug=True, port=5001)