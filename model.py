"""
Phishing Email Detection System

Pipeline:
- Generate synthetic dataset
- Load real dataset (optional)
- Clean text data
- Extract additional features
- Convert text using TF-IDF
- Train Logistic Regression with probability calibration
- Evaluate performance
- Save model, vectorizer, and scaler

FIX: Using CalibratedClassifierCV to prevent extreme 0%/100% predictions.
     Raw Logistic Regression on synthetic-only data can be overconfident.
"""

import pandas as pd
import re
import string
import pickle
import random

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV          # <-- FIX: calibration
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.preprocessing import StandardScaler
from scipy.sparse import hstack


# ─────────────────────────────────────────────
# Step 1: Synthetic Data
# ─────────────────────────────────────────────

phishing_phrases = [
    "urgent account verification needed",
    "update your payment information",
    "click the link to reset your password",
    "your account will be suspended",
    "verify your identity immediately",
    "claim your reward now",
    "unauthorized login attempt detected",
    "limited time offer act now",
    "confirm your billing details",
    "security alert click here",
    "we detected suspicious activity on your account",
    "your password has expired please update now",
    "confirm your information or lose access",
    "you have a pending refund click to claim",
    "dear customer your bank account needs verification",
    "action required your netflix account is on hold",
    "final notice update your payment method",
    "you have been selected for an exclusive reward",
]

legit_phrases = [
    "meeting scheduled for tomorrow",
    "please review the attached document",
    "team lunch on friday",
    "project deadline approaching",
    "your subscription has been renewed",
    "invoice for last month",
    "newsletter latest updates",
    "thank you for your purchase",
    "weekly performance report",
    "good morning hope you are well",
    "just checking in with you",
    "happy birthday best wishes",
    "reminder about the call today",
    "hi team this is a reminder for tomorrows meeting",
    "please review the document before joining",
    "let me know if you have any questions",
    "best regards from your manager",
    "see you at the meeting",
    "the report is attached for your review",
    "quarterly budget discussion scheduled",
    "no action required just a heads up",
    "following up on our last conversation",
    "thanks for your response",
    "welcome to the team",
    "your leave request has been approved",
    "office will be closed on monday",
    "please find the minutes from last meeting",
    "onboarding session tomorrow at noon",
    "feel free to reach out anytime",
    "the presentation is ready for review",
    "HR update new policy document attached",
    "your order has been shipped and will arrive friday",
    "here is your receipt for the recent transaction",
    "the team sync is moved to 3pm today",
]


def generate_email(label):
    """
    Generate a synthetic email.
    label=1 → phishing, label=0 → legitimate
    """
    phrases = phishing_phrases if label == 1 else legit_phrases
    text = " ".join(random.choices(phrases, k=random.randint(3, 6)))
    if label == 1 and random.random() > 0.4:
        # Add a slightly varied fake URL — avoids model memorising exact patterns
        subdomains = ["secure", "verify", "login", "account", "billing", "reset", "confirm"]
        tlds = [".com", ".net", ".xyz", ".top"]
        text += f" http://{random.choice(subdomains)}-{random.randint(100,9999)}{random.choice(tlds)}"
    return text


# Generate 6000 samples for better generalisation
synthetic_data = []
for _ in range(6000):
    label = random.choice([0, 1])
    synthetic_data.append([generate_email(label), label])

df_synth = pd.DataFrame(synthetic_data, columns=["text", "label"])

print("Synthetic phishing samples:", df_synth[df_synth["label"] == 1].shape[0])
print("Synthetic legit samples:   ", df_synth[df_synth["label"] == 0].shape[0])


# ─────────────────────────────────────────────
# Step 2: Load Real Dataset (optional)
# ─────────────────────────────────────────────

try:
    df_real = pd.read_csv("real_emails.csv")
    df_real = df_real[["text", "label"]]
    print("Real dataset loaded:", len(df_real))
except Exception as e:
    print("No real dataset found. Using synthetic only. Reason:", e)
    df_real = pd.DataFrame(columns=["text", "label"])


# Combine & clean
df = pd.concat([df_real, df_synth], ignore_index=True)
df = df.dropna()
df["text"]  = df["text"].astype(str)
df["label"] = df["label"].astype(int)

print("\nTotal dataset:", len(df))
print("  Phishing:", df[df["label"] == 1].shape[0])
print("  Legit:   ", df[df["label"] == 0].shape[0])


# ─────────────────────────────────────────────
# Step 3: Text Cleaning
# ─────────────────────────────────────────────

def clean_text(text):
    """
    Clean email text:
    - lowercase
    - replace URLs/emails with tokens
    - remove numbers and punctuation
    - collapse whitespace
    """
    text = text.lower()
    text = re.sub(r"http\S+", " URLTOKEN ", text)
    text = re.sub(r"\S+@\S+", " EMAILTOKEN ", text)
    text = re.sub(r"\d+", " ", text)
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = re.sub(r"\s+", " ", text).strip()
    return text

df["clean_text"] = df["text"].apply(clean_text)


# ─────────────────────────────────────────────
# Step 4: Feature Engineering
# ─────────────────────────────────────────────

def extract_features(text):
    """
    Hand-crafted features:
    - has_link: URL present
    - has_email: Email address present
    - urgent: word 'urgent' present
    - exclamations: count of !
    - length: total char count
    """
    return [
        int("http" in text or "www" in text),
        int("@" in text),
        int("urgent" in text.lower()),
        text.count("!"),
        len(text)
    ]

extra_features = df["text"].apply(extract_features)
extra_features = pd.DataFrame(
    extra_features.tolist(),
    columns=["has_link", "has_email", "urgent", "exclamations", "length"]
)

scaler       = StandardScaler()
extra_scaled = scaler.fit_transform(extra_features)


# ─────────────────────────────────────────────
# Step 5: TF-IDF Vectorisation
# ─────────────────────────────────────────────

vectorizer = TfidfVectorizer(
    stop_words="english",
    max_features=10000,
    ngram_range=(1, 2)
)

X_text = vectorizer.fit_transform(df["clean_text"])
X      = hstack([X_text, extra_scaled])
y      = df["label"]


# ─────────────────────────────────────────────
# Step 6: Train / Test Split
# ─────────────────────────────────────────────

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)


# ─────────────────────────────────────────────
# Step 7: Train Model with Calibration
#
# WHY CalibratedClassifierCV?
#   Raw LogisticRegression trained on repetitive synthetic phrases
#   becomes overconfident → outputs 99–100% probability.
#   Calibration (Platt scaling via cv=5) corrects the probability
#   curve so confident predictions land around 80–93% instead of 100%.
# ─────────────────────────────────────────────

base_model = LogisticRegression(max_iter=1000, C=1.0)
model      = CalibratedClassifierCV(base_model, cv=5, method="sigmoid")
model.fit(X_train, y_train)


# ─────────────────────────────────────────────
# Step 8: Evaluate
# ─────────────────────────────────────────────

y_pred = model.predict(X_test)

print("\n── Evaluation ──────────────────────────────")
print("Accuracy:", round(accuracy_score(y_test, y_pred) * 100, 2), "%")
print("\nClassification Report:\n", classification_report(y_test, y_pred))
print("\nConfusion Matrix:\n", confusion_matrix(y_test, y_pred))

# Show probability range — confirms no more 100% outputs
y_proba = model.predict_proba(X_test)[:, 1]
print(f"\nPhishing probability range on test set:")
print(f"  Min:  {y_proba.min() * 100:.1f}%")
print(f"  Max:  {y_proba.max() * 100:.1f}%")
print(f"  Mean: {y_proba.mean() * 100:.1f}%")


# ─────────────────────────────────────────────
# Step 9: Save
# ─────────────────────────────────────────────

pickle.dump(model,      open("phishing_model.pkl", "wb"))
pickle.dump(vectorizer, open("vectorizer.pkl",     "wb"))
pickle.dump(scaler,     open("scaler.pkl",         "wb"))

print("\nModel, vectorizer, and scaler saved!")