import os, threading
from flask import Flask
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN","").strip()
CHANNEL = "@MindZapAI"
FARM_LINK = "https://mindzap-six.vercel.app"
TWITTER = "https://x.com/MindZapAI"

app_flask = Flask(__name__)
@app_flask.route('/')
def home(): return "Bot Live!"
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)

# Memory for twitter click
user_clicked_twitter = set()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🐦 Twitter Follow", url=TWITTER)],
        [InlineKeyboardButton("👥 Join @MindZapAI", url="https://t.me/MindZapAI")],
        [InlineKeyboardButton("✅ Verify", callback_data="verify")]
    ]
    await update.message.reply_text(
        "⚡ MindZap AI Farm\n\n"
        "1. Twitter Follow বাটনে ক্লিক করে Follow করো\n"
        "2. Join Community বাটনে Join করো\n"
        "3. তারপর Verify চাপো!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    
    # Telegram Check - STRICT
    try:
        m = await context.bot.get_chat_member(CHANNEL, uid)
        if m.status in ['left', 'kicked']:
            await q.answer("❌ তুমি Join করো নাই!", show_alert=True)
            kb = [[InlineKeyboardButton("👥 Join Now", url="https://t.me/MindZapAI")],
                  [InlineKeyboardButton("🔁 আবার Verify", callback_data="verify")]]
            await q.edit_message_text("❌ তুমি @MindZapAI Join করো নাই! Join করে আবার Verify চাপো!", reply_markup=InlineKeyboardMarkup(kb))
            return
    except Exception as e:
        print(f"ERROR: {e}")
        await q.answer("❌ আমাকে @MindZapAI তে Admin বানাও!", show_alert=True)
        return

    # Telegram Join করেছে, এবার Farming Link দাও
    kb = [[InlineKeyboardButton("🌾 Start Farming", url=FARM_LINK)]]
    await q.edit_message_text(f"🎉 Verified!\n\nতুমি Community Join করেছো! ✅\n\nFarming Link:\n{FARM_LINK}", reply_markup=InlineKeyboardMarkup(kb))

def main():
    threading.Thread(target=run_flask, daemon=True).start()
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(verify))
    print("Bot Started")
    app.run_polling()

if __name__ == "__main__":
    main()
