import os
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import schedule
import time
import threading
import asyncio
from telegram.helpers import escape_markdown

from scraper.job_scraper import scrape_jsearch

# Load .env variables
print("📦 Loading environment variables...")
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Initialize Firebase
try:
    cred = credentials.Certificate("firebase_credentials.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("✅ Firebase connected.")
except Exception as e:
    print("❌ Firebase Error:", e)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hey! I’m your Job Bot 🤖. What would you like to do today?",
        reply_markup=ReplyKeyboardRemove()
    )
    print("👤 User ID:", update.effective_user.id)

# /setrole
async def setrole(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    role = " ".join(context.args)

    if not role:
        await update.message.reply_text("❌ Please provide a role. Example:\n/setrole Software Engineer")
        return

    db.collection("preferences").document(user_id).set({"role": role}, merge=True)
    await update.message.reply_text(f"✅ Job role saved as: *{role}*", parse_mode="Markdown")

# /setlocation
async def setlocation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    location = " ".join(context.args)

    if not location:
        await update.message.reply_text("❌ Please provide a location. Example:\n/setlocation Remote or New York")
        return

    db.collection("preferences").document(user_id).set({"location": location}, merge=True)
    await update.message.reply_text(f"📍 Preferred location saved as: *{location}*", parse_mode="Markdown")

# /showprefs
async def showprefs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    doc = db.collection("preferences").document(user_id).get()

    if doc.exists:
        data = doc.to_dict()
        role = data.get("role", "Not set")
        location = data.get("location", "Not set")
        await update.message.reply_text(
            f"🧠 *Your Preferences:*\n\n🔹 Role: `{role}`\n🔹 Location: `{location}`",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text("ℹ️ No preferences saved yet. Use /setrole and /setlocation to start.")

# /findjobs
async def findjobs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("⚙️ /findjobs command triggered")
    user_id = str(update.effective_user.id)
    doc = db.collection("preferences").document(user_id).get()
    print("📥 Pulled preferences from Firestore")

    if not doc.exists:
        await update.message.reply_text("⚠️ Please set your role and location first using /setrole and /setlocation")
        return

    prefs = doc.to_dict()
    role = prefs.get("role", "")
    location = prefs.get("location", "")

    print(f"🎯 Role: {role} | Location: {location}")
    await update.message.reply_text(f"🔍 Searching for `{role}` jobs in `{location}`...", parse_mode="Markdown")

    jobs = scrape_jsearch(role, location)

    print(f"DEBUG: Found {len(jobs)} jobs")

    if not jobs:
        await update.message.reply_text("❌ No jobs found at the moment.")
        return

    for job in jobs:
        title = escape_markdown(job['title'], version=2)
        company = escape_markdown(job['company'], version=2)
        link = escape_markdown(job['link'], version=2)

        msg = f"*{title}* at _{company}_\n[Apply Here]({link})"
        await update.message.reply_text(msg, parse_mode="MarkdownV2")

# 🔁 Auto-job sender (called by scheduler)
async def send_scheduled_jobs(app: ApplicationBuilder, user_id: int):
    doc = db.collection("preferences").document(str(user_id)).get()
    if not doc.exists:
        print("⚠️ No prefs found for scheduled task")
        return

    prefs = doc.to_dict()
    role = prefs.get("role", "")
    location = prefs.get("location", "")

    print(f"🕒 Auto-Job Search -> {role} in {location}")
    jobs = scrape_jsearch(role, location)

    chat = await app.bot.get_chat(user_id)

    if not jobs:
        await chat.send_message("❌ No new jobs found today.")
        return

    for job in jobs:
        title = escape_markdown(job['title'], version=2)
        company = escape_markdown(job['company'], version=2)
        link = escape_markdown(job['link'], version=2)

        msg = f"*{title}* at _{company}_\n[Apply Here]({link})"
        await chat.send_message(msg, parse_mode="MarkdownV2")

# 🔄 Scheduler setup
def run_schedule(app: ApplicationBuilder):
    user_id = 7730514791  # 👈 Your Telegram ID

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def job():
        await send_scheduled_jobs(app, user_id)

    def schedule_job():
        loop.call_soon_threadsafe(asyncio.create_task, job())

    schedule.every().day.at("02:00").do(schedule_job)

    def start_loop():
        loop.run_forever()

    threading.Thread(target=start_loop, daemon=True).start()

    while True:
        schedule.run_pending()
        time.sleep(1)

# 🚀 Main launcher
def main():
    print("🚀 Starting Telegram bot...")
    try:
        app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("setrole", setrole))
        app.add_handler(CommandHandler("setlocation", setlocation))
        app.add_handler(CommandHandler("showprefs", showprefs))
        app.add_handler(CommandHandler("findjobs", findjobs))
        print("✅ Bot is live! Type /start in Telegram.")
    except Exception as e:
        print("❌ Telegram Error:", e)

    threading.Thread(target=run_schedule, args=(app,), daemon=True).start()
    app.run_polling()

if __name__ == "__main__":
    print("🔥 main() is executing")
    main()
