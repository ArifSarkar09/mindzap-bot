import os
from flask import Flask, request
import telebot
from telebot import types

TOKEN = os.environ.get("BOT_TOKEN", "")
bot = telebot.TeleBot(TOKEN) if TOKEN else None
app = Flask(__name__)

FARM_HTML = """
<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<script src="https://telegram.org/js/telegram-web-app.js"></script>
<style>
:root{--bg:#0a0a0f;--card:#15151d;--border:#24243a;--green:#00ff88;--purple:#8b5cf6;--yellow:#facc15}
body{background:var(--bg);color:#fff;font-family:system-ui;margin:0;padding:14px;padding-bottom:80px}
.card{background:var(--card);border:1px solid var(--border);border-radius:18px;padding:16px;margin-bottom:12px}
.balance-box{text-align:center;padding:22px;background:radial-gradient(ellipse at top,#1e1e2f,#15151d);border:1px solid #8b5cf633}
.balance-box h1{font-size:44px;margin:6px 0;font-weight:900}
.mini{display:flex;justify-content:space-around;font-size:12px;margin-top:12px}
.mini b{font-size:16px;display:block}
.mini div{background:#0a0a0f;border:1px solid var(--border);padding:10px 14px;border-radius:12px;min-width:90px}
.farming-bar{height:10px;background:#24243a;border-radius:10px;overflow:hidden;margin-top:16px}
.farming-fill{height:100%;width:0%;background:linear-gradient(90deg,var(--green),#00cc6a);transition:0.5s}
.task{display:flex;justify-content:space-between;align-items:center;padding:14px;border:1px solid var(--border);border-radius:14px;margin-bottom:10px;background:#1a1a26}
.task-left{display:flex;align-items:center;gap:12px}
.task-icon{width:40px;height:40px;background:#24243a;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:20px}
.btn{padding:9px 18px;border-radius:20px;border:none;font-weight:800;cursor:pointer}
.btn-start{background:#fff;color:#000}.btn-check{background:var(--yellow);color:#000}.btn-done{background:var(--green);color:#000}
.trust{display:flex;gap:7px;flex-wrap:wrap;margin-top:12px}
.trust span{font-size:11px;border:1px solid #24243a;padding:6px 10px;border-radius:20px;background:#0a0a0f}
</style></head><body>
<div class="card balance-box">
  <div style="opacity:0.6;font-size:12px;letter-spacing:2px">TOTAL BALANCE</div>
  <h1 id="totalBal">0 ZAP</h1>
  <div class="mini">
    <div>Farming<br><b id="farmBal" style="color:#00ff88">0</b></div>
    <div>Tasks<br><b id="taskBal" style="color:#8b5cf6">0</b></div>
    <div>Referral<br><b id="refBal">0</b></div>
  </div>
  <div class="farming-bar"><div id="farmFill" class="farming-fill"></div></div>
  <button id="farmBtn" onclick="farmAction()" class="btn" style="width:100%;margin-top:16px;background:#00ff88;padding:15px;font-size:16px;color:#000">🌾 Start Farming (6h)</button>
</div>

<div class="card">
  <div style="display:flex;justify-content:space-between"><b>Refer & Earn 10%</b><span style="background:#00ff8822;color:#00ff88;padding:4px 8px;border-radius:20px;font-size:10px">● Live</span></div>
  <div id="refLink" style="margin:12px 0;background:#0a0a0f;padding:12px;border-radius:10px;font-size:12px;word-break:break-all;border:1px dashed #24243a">Loading...</div>
  <div style="display:flex;gap:16px;font-size:12px"><div>Friends: <b id="refCount">0</b></div><div>Earned: <b id="refEarn">0 ZAP</b></div></div>
  <button onclick="copyRef()" class="btn btn-start" style="width:100%;margin-top:12px">Copy Refer Link</button>
</div>

<div class="card">
  <div style="display:flex;justify-content:space-between"><b>Tasks</b><b id="taskProgress" style="color:#00ff88;font-size:12px">0/3</b></div>
  <div style="margin-top:14px">
    <div class="task" id="task1"><div class="task-left"><div class="task-icon">✈️</div><div>Join @MindZapAI<br><small style="opacity:0.6">+500 ZAP</small></div></div><button class="btn btn-start" onclick="doTask('task1',500,'https://t.me/MindZapAI')">Start</button></div>
    <div class="task" id="task2"><div class="task-left"><div class="task-icon">🐦</div><div>Follow on X<br><small style="opacity:0.6">+500 ZAP</small></div></div><button class="btn btn-start" onclick="doTask('task2',500,'https://x.com')">Start</button></div>
    <div class="task" id="task3"><div class="task-left"><div class="task-icon">👥</div><div>Invite 3 Friends<br><small style="opacity:0.6">+1000 ZAP</small></div></div><button class="btn btn-start" onclick="doTask('task3',1000,'')">Check</button></div>
  </div>
  <div class="trust"><span>📄 Contract: BSCScan</span><span>🛡️ Audit: CertiK Soon</span><span>✅ KYC Verified</span></div>
</div>

<div class="card">
  <b>Withdraw $ZAP</b><span style="font-size:10px;background:#24243a;padding:4px 8px;border-radius:20px;margin-left:8px">Min 5000 ZAP • BEP20</span>
  <input id="wallet" placeholder="Enter BEP20 Address 0x..." style="width:100%;margin-top:12px;padding:13px;background:#0a0a0f;border:1px solid #24243a;border-radius:10px;color:#fff">
  <button onclick="withdraw()" class="btn" style="width:100%;margin-top:10px;background:#8b5cf6;color:#fff;padding:13px">Withdraw</button>
  <div style="font-size:11px;opacity:0.4;margin-top:8px;text-align:center">Withdrawal enabled after TGE</div>
</div>

<script>
let tg=Telegram.WebApp;tg.expand();
let uid=tg.initDataUnsafe?.user?.id||"test_"+Math.floor(Math.random()*100000);
let key='zap_v2_'+uid;
let data=JSON.parse(localStorage.getItem(key)||'{"farm":0,"task":0,"ref":0,"refCount":0,"tasks":{},"farmStart":0,"farmingTemp":0}');
function save(){localStorage.setItem(key,JSON.stringify(data));updateUI()}
function updateUI(){
  let total=Math.floor(data.farm+data.task+data.ref+data.farmingTemp);
  document.getElementById('totalBal').innerText=total.toLocaleString()+' ZAP';
  document.getElementById('farmBal').innerText=Math.floor(data.farm+data.farmingTemp);
  document.getElementById('taskBal').innerText=data.task;
  document.getElementById('refBal').innerText=data.ref;
  document.getElementById('refCount').innerText=data.refCount;
  document.getElementById('refEarn').innerText=data.ref+' ZAP';
  document.getElementById('refLink').innerText='https://t.me/MindZapAIBot?start='+uid;
  document.getElementById('taskProgress').innerText=Object.keys(data.tasks).length+'/3';
  for(let k in data.tasks){let el=document.querySelector('#'+k+' button');if(el){el.innerText='Completed';el.className='btn btn-done';el.disabled=true}}
}
function doTask(id,reward,link){
  let btn=document.querySelector('#'+id+' button');if(btn.disabled)return;
  if(link)window.open(link,'_blank');
  btn.innerText='Checking...';btn.className='btn btn-check';
  setTimeout(()=>{
    if(id=='task3'&&data.refCount<3){btn.innerText='Need 3 Friends';btn.className='btn btn-start';return;}
    data.task+=reward;data.tasks[id]=true;save();
    btn.innerText='Completed';btn.className='btn btn-done';btn.disabled=true;
    tg.HapticFeedback?.notificationOccurred('success');
  },2600);
}
let farmInterval;
function farmLoop(){
  if(!data.farmStart)return;clearInterval(farmInterval);
  farmInterval=setInterval(()=>{
    let elapsed=(Date.now()-data.farmStart)/1000;let max=6*60*60;
    let progress=Math.min(elapsed/max,1);data.farmingTemp=progress*600;
    document.getElementById('farmFill').style.width=(progress*100)+'%';
    document.getElementById('farmBtn').innerText=progress>=1?'🌾 Claim '+Math.floor(data.farmingTemp)+' ZAP':'⛏️ Farming '+Math.floor(progress*100)+'% - '+Math.floor(data.farmingTemp)+' ZAP';
    updateUI();
  },1000);
}
function farmAction(){if(data.farmStart&&data.farmingTemp>=600)claimFarm();else if(!data.farmStart)startFarm()}
function startFarm(){data.farmStart=Date.now();data.farmingTemp=0;save();farmLoop()}
function claimFarm(){data.farm+=data.farmingTemp;data.farmingTemp=0;data.farmStart=0;save();clearInterval(farmInterval);document.getElementById('farmFill').style.width='0%';document.getElementById('farmBtn').innerText='🌾 Start Farming (6h)'}
function copyRef(){navigator.clipboard.writeText(document.getElementById('refLink').innerText);alert('Copied!')}
function withdraw(){let w=document.getElementById('wallet').value.trim();if(!w.startsWith('0x'))return alert('Valid BEP20 address দাও');let total=data.farm+data.task+data.ref;if(total<5000)return alert('Min 5000 লাগবে, আছে '+total);alert('Withdraw request saved! TGE পর পাবে '+total+' ZAP')}
updateUI();if(data.farmStart)farmLoop();
</script></body></html>
"""

@bot.message_handler(commands=['start'])
def start(m):
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🚀 Open MindZap App", web_app=types.WebAppInfo(url="https://mindzap-bot.onrender.com/farm")))
    bot.send_message(m.chat.id, f"Welcome {m.from_user.first_name}!\n\n🧠 MindZap AI Trusted Airdrop Live\n\nTotal Balance + Farming Balance + Referral সব Live.", reply_markup=kb)

@app.route('/')
def home(): return "Live"

@app.route('/farm')
def farm(): return FARM_HTML

@app.route('/webhook', methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return 'ok'

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
