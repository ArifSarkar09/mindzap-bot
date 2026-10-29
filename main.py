import os, threading
from flask import Flask, request
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN","").strip()
CHANNEL = "@MindZapAI"
TWITTER = "https://x.com/MindZapAI"

app_flask = Flask(__name__)

# ==================== FARMING WEBSITE (No Vercel Needed) ====================
FARM_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>MindZap AI</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
    <style>
        *{margin:0;padding:0;box-sizing:border-box}
        body{background:#000;color:#fff;font-family:Arial,sans-serif;text-align:center;padding:20px;min-height:100vh}
        .logo{font-size:50px;margin-top:20px}
        h1{color:#00ff88;margin:10px 0}
        .card{border:2px solid #00ff88;border-radius:20px;padding:25px;margin:30px 10px;background:#0a0a0a}
        .balance{font-size:32px;font-weight:bold;color:#00ff88}
        .btn{background:#00ff88;color:#000;padding:16px 40px;border-radius:12px;font-weight:bold;border:none;font-size:18px;width:90%;margin-top:20px}
        .btn:active{transform:scale(0.95)}
        .task{background:#111;padding:15px;border-radius:12px;margin:10px 0;display:flex;justify-content:space-between;align-items:center}
        .footer{color:#666;margin-top:30px;font-size:13px}
    </style>
</head>
<body>
    <div class="logo">⚡</div>
    <h1>MindZap AI</h1>
    <p>First Viral AI on BSC</p>
    <p id="welcome" style="color:#00ff88;margin-top:10px"></p>

    <div class="card">
        <p>Your $ZAP Balance</p>
        <div class="balance" id="bal">0.00 ZAP</div>
        <p style="margin-top:10px">Farming: <span id="farm">0.000</span>/hr</p>
        <button class="btn" onclick="startFarm()">🌾 Start Farming</button>
    </div>

    <div class="card" style="text-align:left">
        <h3>Tasks</h3>
        <div class="task"><span>👥 Invite 3 Friends</span><span style="color:#00ff88">+1000</span></div>
        <div class="task"><span>🐦 Follow Twitter</span><span style="color:#00ff88">+500</span></div>
    </div>

    <div class="footer">Invite & Earn 100M Airdrop<br>mindzap.ai</div>

<script>
    const tg = window.Telegram.WebApp;
    tg.ready(); tg.expand();
    tg.setHeaderColor('#000000');
    tg.setBackgroundColor('#000000');
    
    const user = tg.initDataUnsafe?.user;
    if(user){
        document.getElementById('welcome').innerText = 'Welcome, ' + user.first_name + '!';
    }

    let balance = parseFloat(localStorage.getItem('zap_bal') || '0');
    let farming = localStorage.getItem('zap_farming') === 'true';
    document.getElementById('bal').innerText = balance.toFixed(3) + ' ZAP';

    function startFarm(){
        if(!farming){
            farming = true;
            localStorage.setItem('zap_farming','true');
            tg.HapticFeedback.notificationOccurred('success');
            alert('Farming Started! Come back after 1 hour');
        } else {
            balance += 0.5;
            localStorage.setItem('zap_bal', balance);
            document.getElementById('bal').innerText = balance.toFixed(3) + ' ZAP';
            tg.HapticFeedback.notificationOccurred('success');
        }
    }
    
    // Auto farm every 3 sec
    setInterval(()=>{
        if(farming){
            let f = parseFloat(document.getElementById('farm').innerText);
            document.getElementById('farm').innerText = (f + 0.001).toFixed(3);
        }
    }, 3000);
</script>
</body>
</html>
"""

@app_flask.route('/')
def home():
    return FARM_HTML

@app_flask.route('/health')
def health():
    return "Bot Live!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)

# ==================== TELEGRAM BOT ====================
def get_farm_url():
    # Render auto URL
    url = os.environ.get("RENDER_EXTERNAL_URL") or os.environ.get("RENDER_EXTERNAL_HOSTNAME")
    if url:
        if not url.startswith("http"): url = "https://" + url
        return url
    # Fallback - get from request not possible here, use hardcoded if needed
    # If not found, bot will use current render domain automatically
    return "https://mindzap-bot.onrender.com"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🐦 Follow Twitter", url=TWITTER)],
        [InlineKeyboardButton("👥 Join Community", url="https://t.me/MindZapAI")],
        [InlineKeyboardButton("✅ Verify", callback_data="verify")]
    ]
    await update.message.reply_text(
        "⚡ Welcome to MindZap AI\nFirst Viral AI on BSC\n\nFarm $ZAP, Invite & Earn 100M Airdrop!\n\nComplete Tasks:\n1. Follow Twitter\n2. Join @MindZapAI\n\nThen click Verify 👇",
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
            await q.edit_message_text("❌ You are NOT in @MindZapAI\n\nPlease Join first, then Verify Again!", reply_markup=InlineKeyboardMarkup(kb))
            return
    except Exception as e:
        print(f"CHAT MEMBER ERROR: {e}")
        await q.answer("Make me ADMIN in @MindZapAI channel!", show_alert=True)
        return

    farm_url = get_farm_url()
    # Use WebApp - opens INSIDE Telegram
    kb = [[InlineKeyboardButton("🌾 Start Farming", web_app=WebAppInfo(url=farm_url))]]
    await q.edit_message_text(
        f"🎉 Verified Successfully!\n\nYour Farming Link is Ready!\nClick Below to Farm Inside Telegram 👇",
        reply_markup=InlineKeyboardMarkup(kb)
    )

def main():
    threading.Thread(target=run_flask, daemon=True).start()
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(verify, pattern="^verify$"))
    print("Bot Started - No Vercel Needed")
    app.run_polling()

if __name__ == "__main__":
    main()
