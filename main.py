FARM_HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<script src="https://telegram.org/js/telegram-web-app.js"></script>
<style>
:root{--bg:#0a0a0a;--card:#171717;--card2:#1f1f1f;--green:#00e676;--text:#fff;--muted:#9ca3af}
*{margin:0;padding:0;box-sizing:border-box;font-family:Inter,sans-serif}
body{background:var(--bg);color:var(--text);padding:16px;padding-bottom:100px}
.top-card{background:linear-gradient(180deg,#1a1a1a,#121212);border:1px solid #262626;border-radius:20px;padding:18px;margin-bottom:16px}
.balance-label{color:var(--muted);font-size:13px}
.balance-main{font-size:36px;font-weight:800;margin:4px 0}
.balance-sub{display:flex;gap:12px;margin-top:8px}
.badge{background:var(--card2);border:1px solid #2a2a2a;padding:6px 12px;border-radius:20px;font-size:12px;color:var(--muted)}
.badge b{color:var(--text)}
.farm-btn{width:100%;margin-top:16px;background:var(--text);color:#000;border:none;padding:16px;border-radius:14px;font-size:16px;font-weight:700}
.farm-btn.farming{background:#2a2a2a;color:var(--muted)}
.card{background:var(--card);border:1px solid #262626;border-radius:20px;padding:16px;margin-bottom:16px}
.card-title{font-weight:700;font-size:16px;margin-bottom:12px}
.ref-link{background:#0e0e0e;border:1px solid #2a2a2a;border-radius:12px;padding:12px;font-size:13px;word-break:break-all;color:#d1d5db}
.btn-row{display:flex;gap:12px;margin-top:12px}
.btn{flex:1;background:var(--card2);border:1px solid #2a2a2a;padding:12px;border-radius:12px;color:var(--text);font-weight:600}
.task{display:flex;justify-content:space-between;align-items:center;background:#1c1c1c;border:1px solid #262626;border-radius:14px;padding:14px;margin-bottom:10px;transition:0.3s}
.task.done{opacity:0.6; border-color:var(--green)}
.task-right{color:var(--green);font-weight:700}
.task small{color:var(--muted);display:block;font-size:11px;margin-top:2px}
.trust-row{display:flex;gap:10px;margin-bottom:16px}
.trust{flex:1;background:var(--card);border:1px solid #262626;border-radius:18px;padding:12px;text-align:center}
.trust p{font-size:12px;color:var(--muted)} .trust b{color:var(--green);font-size:14px}
.trust a{color:var(--green);text-decoration:underline;font-size:13px}
.withdraw-input{width:100%;background:#0e0e0e;border:1px solid #2a2a2a;border-radius:12px;padding:14px;color:#fff;margin-top:10px;outline:none}
.wd-btn{width:100%;margin-top:12px;background:var(--green);color:#000;border:none;padding:14px;border-radius:12px;font-weight:800}
#toast{position:fixed;bottom:20px;left:50%;transform:translateX(-50%);background:#fff;color:#000;padding:10px 18px;border-radius:20px;font-size:13px;font-weight:600;display:none;z-index:99}
</style>
</head>
<body>

<div class="top-card">
  <div class="balance-label">Total Balance</div>
  <div class="balance-main" id="totalBal">0 ZAP</div>
  <div class="balance-sub">
    <div class="badge">Farming: <b id="farmBal">0</b></div>
    <div class="badge">Tasks: <b id="taskBal">0</b></div>
    <div class="badge">Ref: <b id="refCount">0</b></div>
  </div>
  <button class="farm-btn" id="farmBtn" onclick="handleFarm()">Start Farming (6h)</button>
  <div style="text-align:center;color:var(--muted);font-size:12px;margin-top:8px" id="farmTimer"></div>
</div>

<div class="card">
  <div class="card-title">👥 Refer & Earn 10%</div>
  <div style="color:var(--muted);font-size:12px;margin-bottom:10px">You get 10% from every friend's farm</div>
  <div class="ref-link" id="refLink">https://t.me/MindZapAIBot?start=...</div>
  <div class="btn-row">
    <button class="btn" onclick="copyRef()">Copy</button>
    <button class="btn" onclick="shareRef()">Share</button>
  </div>
</div>

<div class="card">
  <div class="card-title">💎 Tasks</div>
  <div id="tasks"></div>
</div>

<div class="trust-row">
  <div class="trust"><p>Contract</p><a href="https://bscscan.com" target="_blank">BSCScan ↗</a></div>
  <div class="trust"><p>Audit</p><b>CertiK Soon</b></div>
  <div class="trust"><p>KYC</p><b>Verified</b></div>
</div>

<div class="card">
  <div class="card-title">💸 Withdraw $ZAP</div>
  <div style="color:var(--muted);font-size:12px">Min: 5000 ZAP | Network: BEP20</div>
  <input id="wallet" class="withdraw-input" placeholder="Paste your BEP20 wallet address">
  <button class="wd-btn" onclick="withdraw()">Withdraw</button>
  <div style="color:var(--muted);font-size:11px;margin-top:8px;text-align:center">Withdrawal enabled after TGE. Points will be converted to on-chain.</div>
</div>

<div id="toast"></div>

<script>
const tg = window.Telegram.WebApp; tg.expand();
const userId = tg.initDataUnsafe?.user?.id || Math.floor(Math.random()*10000000);
const refLinkEl = document.getElementById('refLink');
refLinkEl.innerText = `https://t.me/MindZapAIBot?start=${userId}`;

let data = JSON.parse(localStorage.getItem('mindzap_v2') || '{"total":0,"farm":0,"task":0,"refs":0,"tasksDone":[],"farmStart":0}');

let taskList = [
  {id:'join', name:'Join @MindZapAI', reward:500, link:'https://t.me/MindZapAI', sub:'Telegram Channel'},
  {id:'twitter', name:'Follow Twitter', reward:500, link:'https://x.com', sub:'Follow and RT pinned'},
  {id:'invite3', name:'Invite 3 Friends', reward:1000, link:'', sub:'Invite 3 friends via referral'},
];

function save(){ localStorage.setItem('mindzap_v2', JSON.stringify(data)); renderBalances(); }
function renderBalances(){
  document.getElementById('totalBal').innerText = (data.farm + data.task).toLocaleString() + ' ZAP';
  document.getElementById('farmBal').innerText = data.farm;
  document.getElementById('taskBal').innerText = data.task;
  document.getElementById('refCount').innerText = data.refs;
}
function renderTasks(){
  const wrap = document.getElementById('tasks'); wrap.innerHTML='';
  taskList.forEach(t=>{
    const done = data.tasksDone.includes(t.id);
    const div = document.createElement('div');
    div.className = 'task' + (done?' done':'');
    div.innerHTML = `<div><div>${t.name}</div><small>${t.sub}</small></div><div class="task-right">${done?'✓ Done':'+'+t.reward}</div>`;
    if(!done) div.onclick = ()=>doTask(t);
    wrap.appendChild(div);
  });
}
function doTask(t){
  // Realistic flow
  if(t.id==='invite3' && data.refs < 3){ toast('Need 3 referrals first'); return; }
  if(t.link) window.open(t.link, '_blank');
  const el = event.currentTarget;
  el.innerHTML = `<div><div>${t.name}</div><small>Verifying...</small></div><div class="task-right">⏳</div>`;
  
  setTimeout(()=>{
    data.tasksDone.push(t.id);
    data.task += t.reward;
    data.total = data.farm + data.task;
    save();
    renderTasks();
    toast(`+${t.reward} ZAP Added!`);
    // confetti effect
    el.style.borderColor='#00e676';
  }, 2200);
}
function handleFarm(){
  const now = Date.now();
  if(data.farmStart && now - data.farmStart < 6*60*60*1000){
    toast('Farming already running');
    return;
  }
  if(data.farmStart && now - data.farmStart >= 6*60*60*1000){
    // claim
    const reward = 1000;
    data.farm += reward;
    data.farmStart = 0;
    save();
    toast(`Claimed ${reward} ZAP!`);
    document.getElementById('farmBtn').innerText='Start Farming (6h)';
    return;
  }
  data.farmStart = now;
  save();
  startTimer();
}
function startTimer(){
  const btn = document.getElementById('farmBtn');
  const timerEl = document.getElementById('farmTimer');
  let iv = setInterval(()=>{
    const diff = 6*60*60*1000 - (Date.now() - data.farmStart);
    if(diff<=0){
      clearInterval(iv);
      btn.innerText='Claim 1000 ZAP';
      btn.classList.remove('farming');
      timerEl.innerText='Farming finished!';
      return;
    }
    btn.classList.add('farming');
    btn.innerText='Farming...';
    const h = Math.floor(diff/3600000), m = Math.floor((diff%3600000)/60000), s = Math.floor((diff%60000)/1000);
    timerEl.innerText = `${h}h ${m}m ${s}s left`;
  },1000);
}
function copyRef(){ navigator.clipboard.writeText(refLinkEl.innerText); toast('Referral link copied'); }
function shareRef(){ tg.openTelegramLink(`https://t.me/share/url?url=${encodeURIComponent(refLinkEl.innerText)}&text=Join MindZap AI Mining!`); }
function withdraw(){
  const w = document.getElementById('wallet').value.trim();
  if(w.length<20){ toast('Enter valid BEP20 address'); return; }
  if((data.farm+data.task)<5000){ toast('Minimum 5000 ZAP required'); return; }
  toast('Withdraw request submitted! Will be processed after TGE');
}
function toast(msg){ const t=document.getElementById('toast'); t.innerText=msg; t.style.display='block'; setTimeout(()=>t.style.display='none',2500); }

// referral fake add for demo - backend e real count korbe
if(tg.initDataUnsafe?.start_param){ data.refs++; save(); }

renderBalances(); renderTasks();
if(data.farmStart) startTimer();
</script>
</body>
</html>
"""

# Flask route
@app.route('/farm')
def farm():
    return render_template_string(FARM_HTML)
