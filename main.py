import os, threading
from flask import Flask
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, WebAppInfo
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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🐦 Follow Twitter", url=TWITTER)],
        [InlineKeyboardButton("👥 Join Community", url="https://t.me/MindZapAI")],
        [InlineKeyboardButton("✅ Verify", callback_data="verify")]
    ]
    await update.message.reply_text(
        "⚡ Welcome to MindZap AI - First Viral AI on BSC\n\n"
        "Farm $ZAP, Invite & Earn 100M Airdrop!\n\n"
        "Complete Tasks:\n"
        "1. Follow us on Twitter\n"
        "2. Join Community\n\n"
        "Then click Verify 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    try:
        m = await context.bot.get_chat_member(CHANNEL, uid)
        if m.status in ['left', 'kicked']:
            await q.answer("You haven't joined yet!", show_alert=True)
            kb = [[InlineKeyboardButton("👥 Join Community", url="https://t.me/MindZapAI")],
                  [InlineKeyboardButton("🔁 Verify Again", callback_data="verify")]]
            await q.edit_message_text("❌ You are not in @MindZapAI\n\nPlease join first, then click Verify Again!", reply_markup=InlineKeyboardMarkup(kb))
            return
    except Exception as e:
        print(f"ERROR: {e}")
        await q.answer("Make me admin in @MindZapAI!", show_alert=True)
        return

    # ✅ MINI APP BUTTON - Telegram এর ভিতরেই খুলবে
    kb = [[InlineKeyboardButton("🌾 Start Farming", web_app=WebAppInfo(url=FARM_LINK))]]
    await q.edit_message_text(
        f"🎉 Verified Successfully!\n\nClick Start Farming to open Farm inside Telegram!",
        reply_markup=InlineKeyboardMarkup(kb)
    )

def main():
    threading.Thread(target=run_flask, daemon=True).start()
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(verify))
    print("Bot Started")
    app.run_polling()

if __name__ == "__main__":
    main()
