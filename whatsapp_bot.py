from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import firebase_admin
from firebase_admin import credentials, firestore
from scraper.job_scraper import scrape_jsearch
import os
import json
import re

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

    # Match "position Teacher", "location Florida", case-insensitively
    role_match = re.match(r"position\s*[:\-]?\s*(.+)", incoming_msg, re.IGNORECASE)
    location_match = re.match(r"location\s*[:\-]?\s*(.+)", incoming_msg, re.IGNORECASE)

    if incoming_msg == "find jobs":
        doc = db.collection("preferences").document(user_id).get()

        if not doc.exists:
            msg.body("⚠️ Please set your position and location first.")
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

    elif role_match:
        role = role_match.group(1).strip().title()
        db.collection("preferences").document(user_id).set({"role": role}, merge=True)
        msg.body(f"✅ Position set to: {role}")

    elif location_match:
        location = location_match.group(1).strip().title()
        db.collection("preferences").document(user_id).set({"location": location}, merge=True)
        msg.body(f"📍 Location set to: {location}")

    else:
        msg.body("👋 Hello Beavers, Welcome to *Excuse_us* by Toshif Khan!\n\nUse:\n• Position Teacher\n• Location Florida\n• Find jobs")

    return str(resp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
