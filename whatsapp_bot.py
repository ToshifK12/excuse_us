from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import firebase_admin
from firebase_admin import credentials, firestore
from scraper.job_scraper import scrape_jsearch
import os
import json

app = Flask(__name__)

# Initialize Firebase from env variable
firebase_creds = os.getenv("FIREBASE_CREDS")
cred_dict = json.loads(firebase_creds)
cred = credentials.Certificate(cred_dict)
firebase_admin.initialize_app(cred)
db = firestore.client()

@app.route("/whatsapp", methods=['POST'])
def whatsapp():
    incoming_msg = request.values.get('Body', '').strip().lower()
    user_id = request.values.get('From', '').replace('whatsapp:', '')

    resp = MessagingResponse()
    msg = resp.message()

    if incoming_msg == "find jobs":
        doc = db.collection("preferences").document(user_id).get()

        if not doc.exists:
            msg.body("⚠️ Please set your role and location first.\n\nUse:\n• Set role: Data Analyst\n• Set location: Florida")
            return str(resp)

        prefs = doc.to_dict()
        role = prefs.get("role", "Software Engineer")
        location = prefs.get("location", "Florida")

        jobs = scrape_jsearch(role, location)

        if not jobs:
            msg.body("❌ No jobs found right now.")
        else:
            for job in jobs[:5]:  # Send top 5
                job_text = f"*{job['title']}*\n{job['company']}\nApply: {job['link']}"
                msg.body(job_text)

    elif incoming_msg.startswith("set role:"):
        role = incoming_msg.replace("set role:", "").strip().title()
        db.collection("preferences").document(user_id).set({"role": role}, merge=True)
        msg.body(f"✅ Role set to: {role}")

    elif incoming_msg.startswith("set location:"):
        location = incoming_msg.replace("set location:", "").strip().title()
        db.collection("preferences").document(user_id).set({"location": location}, merge=True)
        msg.body(f"📍 Location set to: {location}")

    elif incoming_msg == "show prefs":
        doc = db.collection("preferences").document(user_id).get()
        if doc.exists:
            prefs = doc.to_dict()
            msg.body(f"🧠 Your Preferences:\n• Role: {prefs.get('role', '-')}\n• Location: {prefs.get('location', '-')}")
        else:
            msg.body("ℹ️ No preferences found.\nUse:\n• Set role: Developer\n• Set location: Florida")

    else:
        msg.body(
            "👋 Hello Beavers! Welcome to *Excuse_us by Toshif Khan* 👨‍💻\n\n"
            "You can control me with:\n"
            "• Set role: Data Analyst\n"
            "• Set location: Florida\n"
            "• Find jobs"
        )

    return str(resp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
