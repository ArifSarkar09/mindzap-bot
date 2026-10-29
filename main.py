import os
import threading
from flask import Flask
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN", "").strip()
CHANNEL = "@MindZapAI"
FARM_LINK = "https://mindzap-six.vercel.app"
TWITTER = "https://x.com/MindZapAI"

# Flask App for Render Free Web Service
app_flask = Flask(__name__)
@app_flask.route('/')
def home():
    return "MindZap Bot is Live!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🐦 Twitter Follow", url=TWITTER)],
        [InlineKeyboardButton("👥 Join Community", url="https://t.me/MindZapAI")],
        [InlineKeyboardButton("✅ Verify", callback_data="verify")]
    ]
    await update.message.reply_text(
        "⚡ MindZap AI - First Viral AI on BSC\n\n"
        "Farm $ZAP, Invite & Earn 100M Airdrop!\n\n"
        "👇 2টা Task করো:\n1. Twitter Follow\n2. Community Join\n\nতারপর Verify ক্লিক করো!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    try:
        m = await context.bot.get_chat_member(CHANNEL, q.from_user.id)
        if m.status in ['member','administrator','creator']:
            kb = [[InlineKeyboardButton("🌾 Start Farming", url=FARM_LINK)]]
            await q.edit_message_text(f"🎉 Verified!\n\nLink:\n{FARM_LINK}", reply_markup=InlineKeyboardMarkup(kb))
        else:
            await q.answer("❌ আগে @MindZapAI Join করো!", show_alert=True)
    except:
        await q.answer("❌ আমাকে @MindZapAI এর Admin বানাও!", show_alert=True)

def main():
    # Start Flask in background
    threading.Thread(target=run_flask, daemon=True).start()
    # Start Bot
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(verify))
    print("Bot Started...")
    app.run_polling()

if __name__ == "__main__":
    main()
