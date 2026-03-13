from flask import Flask, request, jsonify
import pickle
import re
import string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # allow frontend to call backend


# Load trained model & vectorizer

model = pickle.load(open("phishing_model.pkl", "rb"))
vectorizer = pickle.load(open("vectorizer.pkl", "rb"))

# Text cleaning 

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r"http\S+", " URLTOKEN ", text)     # keep link signal
    text = re.sub(r"\S+@\S+", " EMAILTOKEN ", text)  # email signal
    text = re.sub(r"\d+", " ", text)
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = re.sub(r"\s+", " ", text).strip()
    return text


#phishing keywords

PHISHING_KEYWORDS = [
    "urgent",
    "verify",
    "suspended",
    "click",
    "login",
    "confirm",
    "security",
    "account"
]

@app.route("/")
def home():
    return "Phishing Detection API is running!"

# -----------------------------
# Prediction API
# -----------------------------
@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    email_text = data.get("email", "")

    if not email_text.strip():
        return jsonify({"error": "No email provided"}), 400

    cleaned = clean_text(email_text)
    vec = vectorizer.transform([cleaned])

    prediction = model.predict(vec)[0]
    proba = model.predict_proba(vec)[0]

    result = "Phishing" if prediction == 1 else "Legitimate"
    confidence = int(max(proba) * 100)

    flags = []

    # urgency
    if "urgent" in cleaned or "within" in cleaned or "immediately" in cleaned:
        flags.append("Urgency language detected")

    # links
    if "http" in email_text or "www" in email_text:
        flags.append("Link detected in email")

    # phishing keywords
    for word in PHISHING_KEYWORDS:
        if word in cleaned:
            flags.append(f"Phishing keyword detected: '{word}'")
            break

    # confidence control
    if result == "Legitimate":
        confidence = min(confidence, 20)

    if len(flags) == 0:
        confidence = min(confidence, 15)

    return jsonify({
        "result": result,
        "confidence": confidence,
        "flags": flags
    })
if __name__ == "__main__":
    app.run(debug=True)
