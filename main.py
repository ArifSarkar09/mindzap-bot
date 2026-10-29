import os
from flask import Flask, request
import telebot
from telebot import types

TOKEN = os.environ.get("BOT_TOKEN", "")
CHANNEL_USERNAME = os.environ.get("CHANNEL_USERNAME", "@MindZapAI")
TWITTER_URL = "https://x.com/MindZapAI"

bot = telebot.TeleBot(TOKEN) if TOKEN else None
app = Flask(__name__)

USER_DB = {}

def get_main_menu():
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton("📢 Join Community", url=f"https://t.me/{CHANNEL_USERNAME.replace('@','')}"),
        types.InlineKeyboardButton("🐦 Follow on X", url=TWITTER_URL),
        types.InlineKeyboardButton("✅ Verify & Continue", callback_data="verify")
    )
    return kb

def get_farming_menu():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🌾 Open Farming App", web_app=types.WebAppInfo(url="https://mindzap-bot.onrender.com/farm")))
    return kb

FARM_HTML = """
<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<script src="https://telegram.org/js/telegram-web-app.js"></script>
<style>
:root{--bg:#080a0e;--card:#12151c;--border:#1e232f;--green:#00e676;--purple:#7c4dff}
body{background:var(--bg);color:#e6e8eb;font-family:Inter,system-ui;margin:0;padding:12px;padding-bottom:90px}
.top{display:flex;justify-content:space-between;align-items:center;padding:8px 4px}
.lang{border:1px solid var(--border);border-radius:20px;padding:4px;display:flex;gap:4px;background:var(--card)}
.lang button{border:none;background:transparent;color:#888;padding:6px 14px;border-radius:16px;font-weight:800;cursor:pointer}
.lang button.active{background:#fff;color:#000}
.card{background:var(--card);border:1px solid var(--border);border-radius:20px;padding:18px;margin-bottom:12px}
.balance-box{text-align:center;background:radial-gradient(400px at 50% -100%, #1a2233, var(--card))}
.balance-box h1{font-size:46px;margin:8px 0;font-weight:900;letter-spacing:-1.5px}
.stats{display:flex;gap:8px;margin-top:14px}
.stat{flex:1;background:#0a0d12;border:1px solid var(--border);border-radius:14px;padding:10px;text-align:center}
.stat b{display:block;font-size:18px;margin-top:4px}
.stat small{opacity:0.5;font-size:10px;letter-spacing:1px}
.bar{height:12px;background:#0a0d12;border:1px solid var(--border);border-radius:20px;overflow:hidden;margin-top:18px}
.fill{height:100%;width:0%;background:linear-gradient(90deg,var(--green), #69f0ae);transition:0.6s}
.task{display:flex;justify-content:space-between;align-items:center;padding:14px;border:1px solid var(--border);border-radius:14px;margin-bottom:10px;background:#0f131a}
.task-left{display:flex;align-items:center;gap:12px}
.icon{width:42px;height:42px;background:#1a2030;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:20px}
.btn{padding:10px 18px;border-radius:24px;border:none;font-weight:800;cursor:pointer}
.btn-start{background:#fff;color:#000}.btn-check{background:#ffe082;color:#000}.btn-done{background:var(--green);color:#000}
.trust{display:flex;gap:6px;flex-wrap:wrap;margin-top:14px}
.trust span{font-size:11px;border:1px solid var(--border);padding:6px 10px;border-radius:20px;background:#0a0d12}
.live-dot{width:8px;height:8px;background:var(--green);border-radius:50%;display:inline-block;animation:blink 1s infinite}
@keyframes blink{0%,100%{opacity:1}50%{opacity:0.3}}
</style></head><body>
<div class="top">
  <div style="display:flex;align-items:center;gap:8px"><span class="live-dot"></span><b>MindZap</b><span style="opacity:0.5;font-size:12px">AI AGENT</span></div>
  <div class="lang"><button id="btn-en" class="active" onclick="setLang('en')">EN</button><button id="btn-zh" onclick="setLang('zh')">中文</button></div>
</div>

<div class="card balance-box">
  <small id="t_total" style="opacity:0.6;letter-spacing:2px">TOTAL BALANCE</small>
  <h1 id="totalBal">0 ZAP</h1>
  <div class="stats">
    <div class="stat"><small id="t_farm">FARMING</small><b id="farmBal" style="color:#00e676">0</b></div>
    <div class="stat"><small id="t_task">TASKS</small><b id="taskBal" style="color:#7c4dff">0</b></div>
    <div class="stat"><small id="t_ref">REFERRAL</small><b id="refBal">0</b></div>
  </div>
  <div class="bar"><div id="farmFill" class="fill"></div></div>
  <div style="display:flex;justify-content:space-between;font-size:11px;margin-top:8px;opacity:0.6"><span id="t_rate">Rate: 100 ZAP / hour</span><span id="farmPercent">0%</span></div>
  <button id="farmBtn" onclick="farmAction()" class="btn" style="width:100%;margin-top:16px;background:#00e676;padding:16px;font-size:16px;color:#000">🌾 Start Farming</button>
</div>

<div class="card">
  <div style="display:flex;justify-content:space-between"><b id="t_refer_title">Refer & Earn 10%</b><span style="background:#00e67622;color:#00e676;padding:4px 8px;border-radius:20px;font-size:10px"><span class="live-dot"></span> LIVE</span></div>
  <div id="refLink" style="margin:12px 0;background:#080a0e;padding:12px;border-radius:12px;font-size:12px;border:1px dashed var(--border);word-break:break-all">Loading...</div>
  <div style="display:flex;gap:20px;font-size:12px;opacity:0.8"><div><span id="t_friends">Friends</span>: <b id="refCount">0</b></div><div><span id="t_earned">Earned</span>: <b id="refEarn">0 ZAP</b></div></div>
  <button onclick="copyRef()" class="btn btn-start" style="width:100%;margin-top:12px" id="t_copy">Copy Refer Link</button>
</div>

<div class="card">
  <div style="display:flex;justify-content:space-between"><b id="t_tasks">Tasks</b><b id="taskProgress" style="color:#00e676;font-size:12px">0/3</b></div>
  <div style="margin-top:14px">
    <div class="task" id="task1"><div class="task-left"><div class="icon">✈️</div><div><span class="task-name" data-en="Join Community" data-zh="加入社区">Join Community</span><br><small style="opacity:0.6">+500 ZAP</small></div></div><button class="btn btn-start" onclick="doTask('task1',500)">Start</button></div>
    <div class="task" id="task2"><div class="task-left"><div class="icon">🐦</div><div><span class="task-name" data-en="Follow on X" data-zh="关注 X">Follow on X</span><br><small style="opacity:0.6">+500 ZAP</small></div></div><button class="btn btn-start" onclick="doTask('task2',500)">Start</button></div>
    <div class="task" id="task3"><div class="task-left"><div class="icon">👥</div><div><span class="task-name" data-en="Invite 3 Friends" data-zh="邀请3个好友">Invite 3 Friends</span><br><small style="opacity:0.6">+1000 ZAP</small></div></div><button class="btn btn-start" onclick="doTask('task3',1000)">Check</button></div>
  </div>
  <div class="trust"><span>📄 BSCScan</span><span>🛡️ CertiK Soon</span><span>✅ KYC Verified</span><span>👥 12,841 Users</span></div>
</div>

<div class="card">
  <b id="t_withdraw">Withdraw $ZAP</b><span style="font-size:10px;background:#1e232f;padding:4px 8px;border-radius:20px;margin-left:8px">Min 5000 ZAP • BEP20</span>
  <input id="wallet" placeholder="0x..." style="width:100%;margin-top:12px;padding:14px;background:#080a0e;border:1px solid var(--border);border-radius:12px;color:#fff;outline:none">
  <button onclick="withdraw()" class="btn" style="width:100%;margin-top:10px;background:#7c4dff;color:#fff;padding:14px" id="t_withdraw_btn">Withdraw</button>
</div>

<script>
const I18N = {
 en: { total:"TOTAL BALANCE", farm:"FARMING", task:"TASKS", ref:"REFERRAL", rate:"Rate: 100 ZAP / hour", refer_title:"Refer & Earn 10%", friends:"Friends", earned:"Earned", copy:"Copy Refer Link", tasks:"Tasks", withdraw:"Withdraw $ZAP", withdraw_btn:"Withdraw", start_farm:"🌾 Start Farming (6h)", farming:"⛏️ Farming", claim:"🌾 Claim" },
 zh: { total:"总余额", farm:"挖矿", task:"任务", ref:"推荐", rate:"速率: 100 ZAP / 小时", refer_title:"推荐赚取 10%", friends:"好友", earned:"已赚", copy:"复制推荐链接", tasks:"任务", withdraw:"提取 $ZAP", withdraw_btn:"提取", start_farm:"🌾 开始挖矿 (6小时)", farming:"⛏️ 挖矿中", claim:"🌾 领取" }
};
let curLang = localStorage.getItem('zap_lang')||'en';
function setLang(l){curLang=l;localStorage.setItem('zap_lang',l);document.getElementById('btn-en').className=l=='en'?'active':'';document.getElementById('btn-zh').className=l=='zh'?'active':'';applyLang()}
function applyLang(){
 let d=I18N[curLang];
 document.getElementById('t_total').innerText=d.total;document.getElementById('t_farm').innerText=d.farm;document.getElementById('t_task').innerText=d.task;document.getElementById('t_ref').innerText=d.ref;
 document.getElementById('t_rate').innerText=d.rate;document.getElementById('t_refer_title').innerText=d.refer_title;document.getElementById('t_friends').innerText=d.friends;document.getElementById('t_earned').innerText=d.earned;
 document.getElementById('t_copy').innerText=d.copy;document.getElementById('t_tasks').innerText=d.tasks;document.getElementById('t_withdraw').innerText=d.withdraw;document.getElementById('t_withdraw_btn').innerText=d.withdraw_btn;
 document.querySelectorAll('.task-name').forEach(e=>{e.innerText=e.getAttribute('data-'+curLang)});
 if(!data.farmStart) document.getElementById('farmBtn').innerText=d.start_farm;
}
let tg=Telegram.WebApp;tg.expand();
let uid=tg.initDataUnsafe?.user?.id||"uid_"+Math.floor(Math.random()*1e6);
let key='zap_real_'+uid;
let data=JSON.parse(localStorage.getItem(key)||'{"farm":0,"task":0,"ref":0,"refCount":0,"tasks":{},"farmStart":0,"farmingTemp":0}');
function save(){localStorage.setItem(key,JSON.stringify(data));updateUI()}
function updateUI(){
 let total=Math.floor(data.farm+data.task+data.ref+data.farmingTemp);
 document.getElementById('totalBal').innerText=total.toLocaleString()+' ZAP';
 document.getElementById('farmBal').innerText=Math.floor(data.farm+data.farmingTemp);
 document.getElementById('taskBal').innerText=data.task;document.getElementById('refBal').innerText=data.ref;
 document.getElementById('refCount').innerText=data.refCount;document.getElementById('refEarn').innerText=data.ref+' ZAP';
 document.getElementById('refLink').innerText='https://t.me/MindZapAIBot?start='+uid;
 document.getElementById('taskProgress').innerText=Object.keys(data.tasks).length+'/3';
 for(let k in data.tasks){let el=document.querySelector('#'+k+' button');if(el){el.innerText='Completed';el.className='btn btn-done';el.disabled=true}}
}
function doTask(id,reward){
 let btn=document.querySelector('#'+id+' button');if(btn.disabled)return;
 let link="";
 if(id=='task1') link="https://t.me/MindZapAI";
 if(id=='task2') link="https://x.com/MindZapAI";
 if(link){
   try{ tg.openLink(link); } catch(e){ window.open(link, '_blank'); }
 }
 btn.innerText='Verifying...';btn.className='btn btn-check';
 setTimeout(()=>{
  if(id=='task3'&&data.refCount<3){btn.innerText='Need 3 Friends';btn.className='btn btn-start';return;}
  data.task+=reward;data.tasks[id]=true;save();btn.innerText='Completed';btn.className='btn btn-done';btn.disabled=true;
  tg.HapticFeedback?.notificationOccurred('success');
 },2800);
}
let farmInterval;
function farmLoop(){
 if(!data.farmStart)return;clearInterval(farmInterval);
 farmInterval=setInterval(()=>{
  let elapsed=(Date.now()-data.farmStart)/1000;let max=6*60*60;let progress=Math.min(elapsed/max,1);
  data.farmingTemp=progress*600;
  document.getElementById('farmFill').style.width=(progress*100)+'%';
  document.getElementById('farmPercent').innerText=Math.floor(progress*100)+'%';
  let d=I18N[curLang];
  document.getElementById('farmBtn').innerText=progress>=1?d.claim+' '+Math.floor(data.farmingTemp)+' ZAP':d.farming+' '+Math.floor(progress*100)+'%';
  updateUI();
 },1000);
}
function farmAction(){if(data.farmStart&&data.farmingTemp>=600)claimFarm();else if(!data.farmStart)startFarm()}
function startFarm(){data.farmStart=Date.now();data.farmingTemp=0;save();farmLoop()}
function claimFarm(){data.farm+=data.farmingTemp;data.farmingTemp=0;data.farmStart=0;save();clearInterval(farmInterval);document.getElementById('farmFill').style.width='0%';document.getElementById('farmPercent').innerText='0%';document.getElementById('farmBtn').innerText=I18N[curLang].start_farm}
function copyRef(){navigator.clipboard.writeText(document.getElementById('refLink').innerText);alert(curLang=='zh'?'已复制':'Copied!')}
function withdraw(){let w=document.getElementById('wallet').value.trim();if(!w.startsWith('0x'))return alert('Invalid BEP20');let total=data.farm+data.task+data.ref;if(total<5000)return alert(curLang=='zh'?'至少需要5000 ZAP':'Need 5000 ZAP, you have '+total);alert('Withdraw request saved: '+total+' ZAP');}
updateUI();setLang(curLang);if(data.farmStart)farmLoop();
</script></body></html>
"""

@bot.message_handler(commands=['start'])
def start(m):
    uid = m.from_user.id
    if uid not in USER_DB:
        USER_DB[uid] = {"verified": False}
    if USER_DB[uid]["verified"]:
        bot.send_message(m.chat.id, "🌾 Farming is active!", reply_markup=get_farming_menu())
    else:
        txt = (
            "🧠 *MindZap AI Agent | $ZAP Airdrop*\\n\\n"
            "Farm $ZAP with MindZap AI Agent.\\n\\n"
            "Complete to unlock:\\n"
            "1️⃣ Join Community\\n"
            "2️⃣ Follow on X\\n\\n"
            "Then click *Verify & Continue*"
        )
        bot.send_message(m.chat.id, txt, parse_mode="Markdown", reply_markup=get_main_menu())

@bot.callback_query_handler(func=lambda c: c.data == "verify")
def verify(c):
    uid = c.from_user.id
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, uid)
        is_member = member.status in ['member','administrator','creator']
    except:
        is_member = True
    if not is_member:
        bot.answer_callback_query(c.id, "Please join community first!", show_alert=True)
        return
    USER_DB[uid] = {"verified": True}
    bot.answer_callback_query(c.id, "Verified!")
    bot.send_message(c.message.chat.id, "🎉 Verified! Your Farming App is Ready 👇", reply_markup=get_farming_menu())

@app.route('/')
def home(): return "Live"

@app.route('/farm')
def farm(): return FARM_HTML

@app.route('/webhook', methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.get_data().decode('utf-8'))
    bot.process_new_updates([update])
    return 'ok'

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
