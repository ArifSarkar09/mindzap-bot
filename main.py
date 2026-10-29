import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.environ.get("8970687908:AAGtpSAU9Ot3jqgBKAmMYpLUyhzYsSw_o1Y")
CHANNEL = "@MindZapAI"
FARM_LINK = "https://mindzap-six.vercel.app"
TWITTER = "https://x.com/MindZapAI"
COMMUNITY = "https://t.me/MindZapAI"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🐦 Twitter Follow", url=TWITTER)],
        [InlineKeyboardButton("👥 Join Community", url=COMMUNITY)],
        [InlineKeyboardButton("✅ Verify", callback_data="verify")]
    ]
    text = (
        "⚡ MindZap AI - First Viral AI on BSC\n\n"
        "Farm $ZAP, Invite & Earn 100M Airdrop!\n\n"
        "👇 2টা Task করো:\n"
        "1. Twitter Follow\n"
        "2. Community Join\n\n"
        "তারপর Verify ক্লিক করো!"
    )
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    try:
        member = await context.bot.get_chat_member(CHANNEL, q.from_user.id)
        if member.status in ['member', 'administrator', 'creator']:
            kb = [[InlineKeyboardButton("🌾 Start Farming", url=FARM_LINK)]]
            await q.edit_message_text(
                f"🎉 Verified!\n\nতোমার Farming Link:\n{FARM_LINK}",
                reply_markup=InlineKeyboardMarkup(kb)
            )
        else:
            await q.answer("❌ আগে Join করো @MindZapAI তে!", show_alert=True)
    except Exception as e:
        print(e)
        await q.answer("❌ আমাকে @MindZapAI এর Admin বানাও!", show_alert=True)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(verify))
    print("Bot Started...")
    app.run_polling()

if __name__ == "__main__":
    main()
