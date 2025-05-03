from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    incoming_msg = request.values.get("Body", "").lower()
    resp = MessagingResponse()
    msg = resp.message()

    msg.body(f"You said: {incoming_msg}")
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
if __name__ == "__main__":
    print("🔥 WhatsApp bot is running on Flask...")
    app.run(debug=True)
