from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import firebase_admin
from firebase_admin import credentials, firestore
from scraper.job_scraper import scrape_jsearch

app = Flask(__name__)

# Initialize Firebase
cred = credentials.Certificate("firebase_credentials.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

@app.route("/whatsapp", methods=['POST'])
def whatsapp():
    incoming_msg = request.values.get('Body', '').strip().lower()
    user_id = request.values.get('From', '')  # Unique user number from Twilio

    resp = MessagingResponse()
    msg = resp.message()

    if incoming_msg == "find jobs":
        doc = db.collection("preferences").document(user_id).get()

        if not doc.exists:
            msg.body("⚠️ Please set your role and location first.")
            return str(resp)

        prefs = doc.to_dict()
        role = prefs.get("role", "Software Engineer")
        location = prefs.get("location", "Remote")

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
            msg.body(f"🧠 Preferences:\nRole: {prefs.get('role', '-')}\nLocation: {prefs.get('location', '-')}")
        else:
            msg.body("ℹ️ No preferences found. Use:\nSet role: Developer\nSet location: London")

    else:
        msg.body("👋 Welcome to JobBot!\n\nUse:\n• Set role: Data Analyst\n• Set location: Berlin\n• Find jobs\n• Show prefs")

    return str(resp)

if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)

