from flask import Flask, render_template, request, jsonify, session
from groq import Groq
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import json
import re
import requests as http_requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "linkedin-bot-secret-2024")

def get_groq_client(api_key):
    return Groq(api_key=api_key)

def analyze_profile(client, profile_text):
    prompt = f"""You are a LinkedIn profile intelligence expert. Analyze the following LinkedIn profile and extract structured insights.

Profile:
{profile_text}

Return a JSON object with these exact keys:
{{
  "name": "Full name",
  "current_role": "Current job title",
  "company": "Current company",
  "industry": "Industry/domain",
  "location": "Location if available",
  "skills": ["skill1", "skill2", "skill3", "skill4", "skill5"],
  "experience_years": "Estimated years of experience",
  "education": "Highest education",
  "key_achievements": ["achievement1", "achievement2"],
  "personality_traits": ["trait1", "trait2", "trait3"],
  "outreach_angle": "Best angle to approach this person for outreach",
  "summary": "2-sentence professional summary"
}}

Return ONLY valid JSON, no markdown, no explanation."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000,
        temperature=0.3
    )
    raw = response.choices[0].message.content.strip()
    raw = re.sub(r"```json|```", "", raw).strip()
    return json.loads(raw)

def generate_email(client, profile_data, purpose, sender_name, sender_role):
    prompt = f"""You are an expert cold email copywriter. Write a highly personalized outreach email based on this LinkedIn profile intelligence.

Profile Data:
- Name: {profile_data.get('name', 'there')}
- Role: {profile_data.get('current_role', '')}
- Company: {profile_data.get('company', '')}
- Industry: {profile_data.get('industry', '')}
- Key Skills: {', '.join(profile_data.get('skills', [])[:3])}
- Key Achievements: {', '.join(profile_data.get('key_achievements', [])[:2])}
- Best Outreach Angle: {profile_data.get('outreach_angle', '')}

Sender Info:
- Sender Name: {sender_name}
- Sender Role: {sender_role}

Purpose of Email: {purpose}

Write a concise, genuine, personalized cold email. It should:
1. Open with a specific observation about their work (NOT generic flattery)
2. State the purpose clearly in 1-2 sentences
3. Include a soft, low-friction CTA
4. Be under 150 words total
5. Sound human, not robotic

Return JSON:
{{
  "subject": "Email subject line",
  "body": "Full email body"
}}

Return ONLY valid JSON."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=600,
        temperature=0.7
    )
    raw = response.choices[0].message.content.strip()
    raw = re.sub(r"```json|```", "", raw).strip()
    return json.loads(raw)

def chat_with_ai(client, message, profile_data, chat_history):
    system_prompt = f"""You are a LinkedIn Profile Intelligence Assistant. You have analyzed the following profile:

{json.dumps(profile_data, indent=2)}

Help the user:
- Answer questions about this profile
- Suggest outreach strategies
- Refine or rewrite emails
- Provide networking advice
- Analyze the person's professional background

Be concise, insightful, and actionable."""

    messages = [{"role": "system", "content": system_prompt}]
    for msg in chat_history[-6:]:
        messages.append(msg)
    messages.append({"role": "user", "content": message})

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=500,
        temperature=0.7
    )
    return response.choices[0].message.content

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/analyze", methods=["POST"])
def analyze():
    data = request.json
    api_key = data.get("api_key", "").strip()
    profile_text = data.get("profile_text", "").strip()

    if not api_key:
        return jsonify({"error": "Groq API key is required"}), 400
    if not profile_text or len(profile_text) < 50:
        return jsonify({"error": "Please provide a more detailed LinkedIn profile"}), 400

    try:
        client = get_groq_client(api_key)
        profile_data = analyze_profile(client, profile_text)
        session["profile_data"] = profile_data
        session["api_key"] = api_key
        session["chat_history"] = []
        return jsonify({"success": True, "profile": profile_data})
    except json.JSONDecodeError:
        return jsonify({"error": "AI returned invalid response. Try again."}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/generate-email", methods=["POST"])
def gen_email():
    data = request.json
    profile_data = session.get("profile_data")
    api_key = session.get("api_key")

    if not profile_data:
        return jsonify({"error": "Please analyze a profile first"}), 400

    purpose = data.get("purpose", "networking")
    sender_name = data.get("sender_name", "")
    sender_role = data.get("sender_role", "")

    try:
        client = get_groq_client(api_key)
        email_data = generate_email(client, profile_data, purpose, sender_name, sender_role)
        return jsonify({"success": True, "email": email_data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    message = data.get("message", "").strip()
    profile_data = session.get("profile_data")
    api_key = session.get("api_key")
    chat_history = session.get("chat_history", [])

    if not profile_data:
        return jsonify({"error": "Please analyze a profile first"}), 400
    if not message:
        return jsonify({"error": "Message is required"}), 400

    try:
        client = get_groq_client(api_key)
        reply = chat_with_ai(client, message, profile_data, chat_history)
        chat_history.append({"role": "user", "content": message})
        chat_history.append({"role": "assistant", "content": reply})
        session["chat_history"] = chat_history[-12:]
        return jsonify({"success": True, "reply": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/send-email", methods=["POST"])
def send_email():
    data = request.json
    smtp_email = data.get("smtp_email", "").strip()
    smtp_password = data.get("smtp_password", "").strip()
    to_email = data.get("to_email", "").strip()
    subject = data.get("subject", "").strip()
    body = data.get("body", "").strip()

    if not all([smtp_email, smtp_password, to_email, subject, body]):
        return jsonify({"error": "All email fields are required"}), 400

    try:
        msg = MIMEMultipart()
        msg["From"] = smtp_email
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(smtp_email, smtp_password)
            server.sendmail(smtp_email, to_email, msg.as_string())

        return jsonify({"success": True, "message": "Email sent successfully!"})
    except smtplib.SMTPAuthenticationError:
        return jsonify({"error": "Gmail authentication failed. Use an App Password (not your regular password)."}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/jobs", methods=["POST"])
def search_jobs():
    data = request.json
    profile_data = session.get("profile_data")
    api_key = session.get("api_key")

    if not profile_data:
        return jsonify({"error": "Please analyze a profile first"}), 400

    skills = profile_data.get("skills", [])
    role = profile_data.get("current_role", "software engineer")
    industry = profile_data.get("industry", "technology")

    # Fetch real jobs from Remotive API (free, no key needed)
    real_jobs = []
    try:
        search_term = skills[0] if skills else "software"
        resp = http_requests.get(
            f"https://remotive.com/api/remote-jobs?search={search_term}&limit=6",
            timeout=8
        )
        if resp.status_code == 200:
            jobs_data = resp.json().get("jobs", [])
            for j in jobs_data[:6]:
                real_jobs.append({
                    "title": j.get("title", ""),
                    "company": j.get("company_name", ""),
                    "location": j.get("candidate_required_location", "Remote"),
                    "url": j.get("url", ""),
                    "salary": j.get("salary", "Not specified"),
                    "tags": j.get("tags", [])[:4],
                    "source": "Remotive"
                })
    except Exception:
        pass

    # Use Groq to suggest top Indian companies hiring for this profile
    try:
        client = get_groq_client(api_key)
        prompt = f"""Based on this professional profile, suggest 6 top companies in India actively hiring for similar roles.

Profile:
- Current Role: {role}
- Industry: {industry}
- Skills: {', '.join(skills[:5])}

Return a JSON array of 6 companies:
[
  {{
    "company": "Company Name",
    "role": "Best matching job title",
    "location": "City, India",
    "why": "One sentence why this is a great match",
    "naukri_search": "search keyword for naukri.com",
    "linkedin_search": "search keyword for linkedin jobs"
  }}
]

Focus on real, well-known companies in India. Return ONLY valid JSON array."""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.5
        )
        raw = response.choices[0].message.content.strip()
        raw = re.sub(r"```json|```", "", raw).strip()
        ai_companies = json.loads(raw)
    except Exception:
        ai_companies = []

    return jsonify({
        "success": True,
        "remote_jobs": real_jobs,
        "india_companies": ai_companies,
        "profile_role": role,
        "profile_skills": skills[:5]
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)
