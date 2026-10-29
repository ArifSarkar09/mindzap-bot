import os, threading
from flask import Flask, request
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN","").strip()
CHANNEL = "@MindZapAI"
TWITTER = "https://x.com/MindZapAI"

app_flask = Flask(__name__)

FARM_HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>MindZap AI - Farming</title>
<script src="https://telegram.org/js/telegram-web-app.js"></script>
<meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=no">
<style>
:root{--green:#00ff88;--bg:#070707;--card:#121212;--border:#222}
*{margin:0;padding:0;box-sizing:border-box;font-family:system-ui}
body{background:var(--bg);color:#fff;padding:15px}
.header{display:flex;justify-content:space-between;align-items:center;padding:10px 0}
.badge{background:var(--green);color:#000;padding:4px 10px;border-radius:20px;font-size:12px;font-weight:bold}
.card{background:var(--card);border:1px solid var(--border);border-radius:20px;padding:20px;margin:15px 0}
.balance{font-size:36px;font-weight:900;color:var(--green)}
.small{color:#888;font-size:13px}
.btn{width:100%;padding:16px;border-radius:14px;border:none;font-weight:bold;font-size:16px;margin-top:12px}
.btn-green{background:var(--green);color:#000}
.btn-dark{background:#1e1e1e;color:#fff;border:1px solid var(--border)}
.row{display:flex;gap:10px;margin-top:10px}
.stat{flex:1;background:#0f0f0f;padding:12px;border-radius:12px;text-align:center}
.stat b{display:block;color:var(--green);font-size:18px}
.task{display:flex;justify-content:space-between;align-items:center;padding:14px;background:#0f0f0f;border-radius:12px;margin:8px 0}
.live{height:120px;overflow:hidden;background:#0a0a0a;border-radius:12px;padding:10px;font-size:13px}
.input{width:100%;padding:14px;border-radius:10px;background:#000;border:1px solid var(--border);color:#fff;margin-top:10px}
</style>
</head>
<body>
<div class="header">
  <div><b>⚡ MindZap AI</b><div class="small">Verified on BSC</div></div>
  <div class="badge">● LIVE</div>
</div>

<div class="card" style="text-align:center">
  <div class="small">Total $ZAP Farmed</div>
  <div class="balance" id="bal">0.00</div>
  <div class="small" id="uname">Loading...</div>
  <div class="row">
    <div class="stat"><span class="small">Farming</span><b id="rate">0.000/h</b></div>
    <div class="stat"><span class="small">Referrals</span><b id="refCount">0</b></div>
  </div>
  <button class="btn btn-green" id="farmBtn" onclick="farm()">🌾 Start Farming (6h)</button>
  <div class="small" id="timer" style="margin-top:8px"></div>
</div>

<div class="card">
  <b>👥 Refer & Earn 10%</b>
  <div class="small" style="margin:6px 0">You get 10% from every friend's farm</div>
  <input class="input" id="refLink" readonly>
  <div class="row">
    <button class="btn btn-dark" style="flex:1" onclick="copyRef()">Copy</button>
    <button class="btn btn-dark" style="flex:1" onclick="shareRef()">Share</button>
  </div>
</div>

<div class="card">
  <b>💎 Tasks</b>
  <div class="task"><span>Join @MindZapAI</span><b style="color:var(--green)">+500</b></div>
  <div class="task"><span>Follow Twitter</span><b style="color:var(--green)">+500</b></div>
  <div class="task"><span>Invite 3 Friends</span><b style="color:var(--green)">+1000</b></div>
</div>

<div class="row">
  <div class="card" style="flex:1;text-align:center"><div class="small">Contract</div><a href="#" style="color:var(--green);font-size:12px">BSCScan ↗</a></div>
  <div class="card" style="flex:1;text-align:center"><div class="small">Audit</div><span style="color:var(--green)">CertiK Soon</span></div>
  <div class="card" style="flex:1;text-align:center"><div class="small">KYC</div><span style="color:var(--green)">Verified</span></div>
</div>

<div class="card">
  <b>💸 Withdraw $ZAP</b>
  <div class="small">Min: 5000 ZAP | Network: BEP20</div>
  <input class="input" id="wallet" placeholder="Paste your BEP20 wallet address">
  <button class="btn btn-green" onclick="withdraw()">Withdraw to Wallet</button>
  <div class="small" style="margin-top:8px">Withdrawal enabled after TGE (Nov 2026). Your balance is safe.</div>
</div>

<div class="card">
  <b>🔴 Live Activity</b>
  <div class="live" id="live"></div>
</div>

<script>
const tg = Telegram.WebApp; tg.ready(); tg.expand();
const user = tg.initDataUnsafe?.user;
let uid = user?.id || Math.floor(Math.random()*1000000);
let bal = parseFloat(localStorage.getItem('zap_'+uid)||'0');
let refs = parseInt(localStorage.getItem('ref_'+uid)||'0');
let farmingUntil = parseInt(localStorage.getItem('farmUntil_'+uid)||'0');

document.getElementById('uname').innerText = user ? `Welcome, ${user.first_name}` : `ID: ${uid}`;
document.getElementById('bal').innerText = bal.toFixed(3);
document.getElementById('refCount').innerText = refs;
document.getElementById('refLink').value = `https://t.me/MindZapAIBot?start=${uid}`;

// Check referral from start_param
const startParam = tg.initDataUnsafe?.start_param;
if(startParam && startParam!=uid){
  // In real app, call your backend to add referral
  console.log('Referred by', startParam);
}

function farm(){
  const now = Date.now();
  if(farmingUntil > now){ tg.HapticFeedback.notificationOccurred('warning'); return; }
  farmingUntil = now + 6*3600*1000;
  localStorage.setItem('farmUntil_'+uid, farmingUntil);
  tg.HapticFeedback.notificationOccurred('success');
  tick();
}
function tick(){
  const now = Date.now();
  if(farmingUntil > now){
    let left = farmingUntil - now;
    let h = Math.floor(left/3600000), m = Math.floor((left%3600000)/60000), s = Math.floor((left%60000)/1000);
    document.getElementById('timer').innerText = `Farming ends in ${h}h ${m}m ${s}s`;
    document.getElementById('rate').innerText = '0.500/h';
    document.getElementById('farmBtn').innerText = '⛏️ Farming...';
    // auto add balance slowly
    bal += 0.0001; localStorage.setItem('zap_'+uid, bal);
    document.getElementById('bal').innerText = bal.toFixed(3);
  } else {
    document.getElementById('timer').innerText = 'Click Start to Farm';
    document.getElementById('farmBtn').innerText = '🌾 Start Farming (6h)';
    document.getElementById('rate').innerText = '0.000/h';
  }
}
setInterval(tick,1000); tick();

function copyRef(){ navigator.clipboard.writeText(document.getElementById('refLink').value); tg.HapticFeedback.notificationOccurred('success'); alert('Referral Link Copied!'); }
function shareRef(){ tg.openTelegramLink(`https://t.me/share/url?url=${encodeURIComponent(document.getElementById('refLink').value)}&text=Farm $ZAP with me!`); }
function withdraw(){
  let w = document.getElementById('wallet').value;
  if(w.length < 10){ alert('Enter valid BEP20 address'); return; }
  if(bal < 5000){ alert(`Minimum 5000 ZAP needed. You have ${bal.toFixed(2)}`); return; }
  alert('✅ Withdraw request submitted!\\nPayout after TGE. Balance is locked safely.');
}

// Fake live feed for trust
const names = ['Arif','Sakib','Rahman','Alex','John','CryptoKing','Aisha'];
const live = document.getElementById('live');
setInterval(()=>{
  let n = names[Math.floor(Math.random()*names.length)];
  let amt = (Math.random()*200+50).toFixed(0);
  let div = document.createElement('div');
  div.innerHTML = `🟢 ${n}*** withdrew ${amt} ZAP - 2s ago`;
  live.prepend(div);
  if(live.children.length>6) live.lastChild.remove();
}, 2500);
</script>
</body>
</html>
"""

@app_flask.route('/')
def home(): return FARM_HTML
@app_flask.route('/health')
def health(): return "OK"

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
        "⚡ Welcome to MindZap AI\n\nFarm $ZAP, Invite & Earn!\n\nComplete Tasks:\n1. Follow Twitter\n2. Join @MindZapAI\nThen Verify 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    try:
        m = await context.bot.get_chat_member(CHANNEL, q.from_user.id)
        if m.status in ['left','kicked']:
            await q.edit_message_text("❌ Join @MindZapAI first!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("👥 Join", url="https://t.me/MindZapAI")],[InlineKeyboardButton("🔁 Verify Again", callback_data="verify")]]))
            return
    except:
        await q.answer("Make me ADMIN in @MindZapAI", show_alert=True); return
    
    url = os.environ.get("RENDER_EXTERNAL_URL") or f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME','')}"
    if not url.startswith("http"): url = "https://" + url
    kb = [[InlineKeyboardButton("🌾 Open Farming App", web_app=WebAppInfo(url=url))]]
    await q.edit_message_text("🎉 Verified! Your Trusted Farming App is Ready 👇", reply_markup=InlineKeyboardMarkup(kb))

def main():
    threading.Thread(target=run_flask, daemon=True).start()
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(verify, pattern="^verify$"))
    app.run_polling()

if __name__ == "__main__": main()
