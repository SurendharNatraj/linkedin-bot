# 🔗 LinkedIn Profile Intelligence & Automated Email Outreach Bot

A Gen AI-powered web application that analyzes LinkedIn profiles and generates personalized outreach emails using **Groq AI (LLaMA 3.3 70B)**.

---

## 🚀 Features

- **Profile Intelligence** — Paste any LinkedIn profile text and get structured AI analysis (skills, achievements, personality, outreach angle)
- **Personalized Email Generation** — Auto-generate tailored cold emails based on profile insights
- **AI Chatbot** — Chat with the AI about the profile, refine emails, get strategy advice
- **Email Sending** — Send emails directly via Gmail SMTP from the app
- **Beautiful Dark UI** — Professional, responsive web interface

---

## 🛠️ Setup Instructions

### Step 1: Install Python
Make sure Python 3.8+ is installed. Download from https://python.org

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Get Your Groq API Key
1. Go to https://console.groq.com
2. Sign up / Log in
3. Create a new API key
4. Copy the key (starts with `gsk_...`)

### Step 4: Run the App
```bash
python app.py
```

### Step 5: Open in Browser
Go to: **http://localhost:5000**

---

## 📧 Gmail Setup for Email Sending

To send emails, you need a **Gmail App Password** (NOT your regular password):

1. Go to your Google Account → Security
2. Enable 2-Step Verification (if not done)
3. Go to: https://myaccount.google.com/apppasswords
4. Create an App Password for "Mail"
5. Use this 16-character password in the app

---

## 🎯 How to Use

1. **Enter Groq API Key** in the sidebar
2. **Paste LinkedIn Profile** text (copy from LinkedIn profile page)
3. **Click "Analyze Profile"** → Get full AI intelligence report
4. **Fill in your details** (name, role, purpose)
5. **Click "Generate Email"** → Get a personalized cold email
6. **Chat** with the AI to refine the email further
7. **Send Email** using Gmail SMTP

---

## 📁 Project Structure

```
linkedin-bot/
├── app.py              # Flask backend + Groq AI integration
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
├── README.md           # This file
└── templates/
    └── index.html      # Full web UI
```

---

## 🔧 Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python + Flask |
| AI Model | Groq API (LLaMA 3.3 70B) |
| Frontend | HTML5 + CSS3 + Vanilla JS |
| Email | Gmail SMTP |
| Fonts | Google Fonts (Syne + DM Sans) |

---

## ⚠️ Notes

- LinkedIn profile text must be pasted manually (direct scraping violates LinkedIn ToS)
- Groq API is free with generous rate limits
- Gmail App Password required for email sending
- Session data is stored server-side per browser session

---

## 👩‍💻 Developed By

Department of Information Technology  
Second Review Project - 2024-2025
