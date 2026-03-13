import pandas as pd
import re
import string
import pickle
import random
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

# -----------------------------
# Step 1: Synthetic data setup
# -----------------------------
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
    "we detected suspicious activity",
    "login to secure your account",
    "your mailbox will be closed",
    "confirm your account to avoid suspension",
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
    "happy birthday from all of us",
    "your order has been shipped",
    "minutes of the meeting attached",
    "schedule for next week",
    "payment received successfully",
]

def generate_email(label):
    if label == 1:  # phishing
        num_phrases = random.randint(3, 7)
        text = " ".join(random.choices(phishing_phrases, k=num_phrases))
        # add fake link sometimes
        if random.random() > 0.5:
            text += " http://verify-login-secure" + str(random.randint(100, 999)) + ".com"
        return text
    else:  # legit
        num_phrases = random.randint(3, 7)
        text = " ".join(random.choices(legit_phrases, k=num_phrases))
        return text

# Generate synthetic dataset
synthetic_samples = 6000
synthetic_data = []
for _ in range(synthetic_samples):
    label = random.choices([0, 1], weights=[0.7, 0.3])[0]  # 70% legit, 30% phishing
    synthetic_data.append([generate_email(label), label])

df_synth = pd.DataFrame(synthetic_data, columns=["text", "label"])
print("Synthetic samples:", len(df_synth))

# -----------------------------
# Step 2: Load real dataset
# -----------------------------
try:
    df_real = pd.read_csv("real_emails.csv")
    df_real = df_real[["text", "label"]]
    print("Real samples:", len(df_real))
except Exception as e:
    print(" Could not load real_emails.csv:", e)
    print("Proceeding with only synthetic data...")
    df_real = pd.DataFrame(columns=["text", "label"])

# -----------------------------
# Step 3: Combine datasets
# -----------------------------
df = pd.concat([df_synth, df_real], ignore_index=True)
df = df.sample(frac=1).reset_index(drop=True)  # shuffle
print("Total dataset size:", len(df))

# -----------------------------
# Step 3.1: Remove missing values & ensure proper types
# -----------------------------
df = df.dropna(subset=["label", "text"])
df["label"] = df["label"].astype(int)
df["text"] = df["text"].astype(str)
print("Dataset size after removing missing labels/text:", len(df))

# -----------------------------
# Step 4: Clean text
# -----------------------------
def clean_text(text):
    text = text.lower()
    text = re.sub(r"http\S+", " ", text)        # remove URLs
    text = re.sub(r"\S+@\S+", " ", text)       # remove emails
    text = re.sub(r"\d+", " ", text)           # remove numbers
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = re.sub(r"\s+", " ", text).strip()
    return text

df["text"] = df["text"].apply(clean_text)

# -----------------------------
# Step 5: Vectorization (TF-IDF with n-grams)
# -----------------------------
X = df["text"]
y = df["label"]

vectorizer = TfidfVectorizer(
    stop_words="english",
    max_features=10000,
    ngram_range=(1, 2)  # unigrams + bigrams
)

X_vec = vectorizer.fit_transform(X)

# -----------------------------
# Step 6: Train-test split (stratified)
# -----------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X_vec, y, test_size=0.2, random_state=42, stratify=y
)

# -----------------------------
# Step 7: Train model (Logistic Regression)
# -----------------------------
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

# -----------------------------
# Step 8: Evaluate
# -----------------------------
y_pred = model.predict(X_test)

print("\nAccuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))
print("\nConfusion Matrix:\n", confusion_matrix(y_test, y_pred))

# -----------------------------
# Step 9: Save model and vectorizer
# -----------------------------
pickle.dump(model, open("phishing_model.pkl", "wb"))
pickle.dump(vectorizer, open("vectorizer.pkl", "wb"))

print("\n Model and vectorizer saved successfully!")

