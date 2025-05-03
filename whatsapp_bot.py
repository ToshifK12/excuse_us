from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import firebase_admin
from firebase_admin import credentials, firestore
from scraper.job_scraper import scrape_jsearch
import os
import json
import traceback

app = Flask(__name__)

# Initialize Firebase from env variable
firebase_creds = os.getenv("FIREBASE_CREDS")
cred_dict = json.loads(firebase_creds)
cred = credentials.Certificate(cred_dict)
firebase_admin.initialize_app(cred)
db = firestore.client()

@app.route("/whatsapp", methods=['POST'])
def whatsapp():
    try:
        incoming_msg = request.values.get('Body', '').strip().lower()
        user_id = request.values.get('From', '').replace('whatsapp:', '')
        print(f"[INCOMING] From: {user_id} | Message: {incoming_msg}")  # Debug log

        resp = MessagingResponse()
        msg = resp.message()

        if incoming_msg == "find jobs":
            doc = db.collection("preferences").document(user_id).get()

            if not doc.exists:
                msg.body("⚠️ Please set your role and location first.")
                print("[INFO] No preferences set")
                return str(resp)

            prefs = doc.to_dict()
            role = prefs.get("role", "Software Engineer")
            location = prefs.get("location", "Remote")

            print(f"[INFO] Searching jobs for Role: {role}, Location: {location}")
            jobs = scrape_jsearch(role, location)

            if not jobs:
                msg.body("❌ No jobs found right now.")
                print("[INFO] No jobs found")
            else:
                for job in jobs[:5]:  # Send top 5
                    job_text = f"*{job['title']}*\n{job['company']}\nApply: {job['link']}"
                    msg.body(job_text)

        elif incoming_msg.startswith("set role:"):
            role = incoming_msg.replace("set role:", "").strip().title()
            db.collection("preferences").document(user_id).set({"role": role}, merge=True)
            msg.body(f"✅ Role set to: {role}")
            print(f"[UPDATE] Role set to {role} for {user_id}")

        elif incoming_msg.startswith("set location:"):
            location = incoming_msg.replace("set location:", "").strip().title()
            db.collection("preferences").document(user_id).set({"location": location}, merge=True)
            msg.body(f"📍 Location set to: {location}")
            print(f"[UPDATE] Location set to {location} for {user_id}")

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

    except Exception as e:
        print("[ERROR] Exception occurred:", str(e))
        traceback.print_exc()
        # Reply with generic error message to user
        resp = MessagingResponse()
        resp.message("⚠️ An error occurred. Please try again later.")
        return str(resp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
