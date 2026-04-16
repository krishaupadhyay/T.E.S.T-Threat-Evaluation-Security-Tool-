#  T.E.S.T. — Threat Evaluation Security Tool  
**AI-Powered Cybersecurity Platform for Beginners and Small Organizations**

---

## 📌 Overview

T.E.S.T. (Threat Evaluation Security Tool) is a web-based cybersecurity platform designed to make threat detection simple, accessible, and practical.

It combines machine learning, natural language processing, and web security analysis into a single dashboard. The goal is to help users identify threats, understand them clearly, and take appropriate action without needing deep technical knowledge.

This project is especially useful for students, beginners, and small organizations who find existing tools too complex or expensive.

---

## 🎯 Key Features

### 📧 Email Phishing Analyzer (EPA)

This module analyzes email content to detect phishing attempts using a machine learning model based on TF-IDF and Logistic Regression (~92% accuracy).

**The system checks for:**
- Fake or misleading domains  
- Suspicious links  
- Urgency or scam-related language  

**It provides:**
- Risk score (0–95%)  
- Risk level (Low / Medium / High)  
- Highlighted suspicious content  

---

### 🌐 Web Vulnerability Scanner (WVS)

This module scans websites safely and checks for common security issues.

**It detects:**
- SQL Injection  
- Cross-Site Scripting (XSS)  
- Missing security headers (CSP, HSTS, X-Frame-Options)  

**The output includes:**
- Severity levels (Low → Critical)  
- Simple explanations  
- Suggested fixes  

---

### 🧠 AI Intelligence Core

This is the core logic of the system. It processes inputs from both modules using ML and NLP techniques.

**It generates:**
- Risk scores  
- Clear explanations  
- Practical recommendations  

---

### 📊 Unified Dashboard

All features are available in one place through a simple and clean interface.  
Users can run scans, view results, and understand outputs without confusion.

---

### 🔐 Authentication System

- Secure login with email and password  
- OTP-based verification  
- Encrypted credential handling  

---

## 🏗️ System Architecture

```text
Frontend (HTML + Tailwind CSS)
        ↓
Backend (Node.js + Express.js)
        ↓
AI Service (Python Flask)
        ↓
Database (MongoDB)
```

- Modular three-layer architecture  
- Communication via REST APIs  
- Scalable and maintainable design  

---

## 🛠️ Tech Stack

| Category            | Technology Used |
|--------------------|----------------|
| Frontend           | HTML, CSS, Tailwind CSS |
| Backend            | Node.js, Express.js |
| AI Service         | Python, Flask |
| Machine Learning   | Logistic Regression, TF-IDF |
| Web Scanning       | Pre-trained Models |
| Database           | MongoDB |
| Authentication     | JWT, OTP |

---

## ⚙️ Installation and Setup

### Clone Repository

```bash
git clone https://github.com/krishaupadhyay/TEST-Final-project.git
cd TEST-Final-project
```

---

### Backend Setup

```bash
cd backend
npm install
npm start
```

---

### AI Service Setup

```bash
cd ai-service
pip install -r requirements.txt
python app.py
```

---

### Frontend

```bash
# Open directly
index.html

# OR use Live Server (recommended)
```

---

## 📈 Performance

- Phishing detection accuracy: ~92%  
- Email analysis time: Few seconds  
- Web scan time: 15–25 seconds  
- Fast dashboard loading with real-time updates  

---

## 🧪 Testing

The project includes:

- Unit Testing  
- Integration Testing  
- System Testing  

Each module was tested individually and then validated as a complete system using real-world scenarios.

---

## ⚠️ Challenges Solved

- Improved overconfident ML predictions using probability calibration  
- Optimized long email handling with smart input limits  
- Resolved backend ↔ AI service communication issues (CORS)  
- Improved detection accuracy through better dataset selection  

---

## 🔮 Future Improvements

- Support for more OWASP vulnerabilities  
- Browser extension for real-time detection  
- PDF report generation  
- Integration with threat intelligence APIs  
- Dashboard with scan history and analytics  

---

## 📸 Screenshots (Add Your Images Here)

```markdown
![Dashboard](./screenshots/dashboard.png)
![Phishing Result](./screenshots/phishing.png)
![Web Scan](./screenshots/webscan.png)
```

---

## 👥 Team

- Prachi Rana  
- Krisha Upadhyay  
- Nandan Vakani  
- Harshil Patel  

**Guided by:** Prof. Ashish Katira  
