"""V38: 선생님(반)마다 작전방 따로 쓰기 — 작전 코드
지금까지는 작전이 저장소의 문서 하나(rooms/current)뿐이라, 어느 선생님이 열든 같은 방이었음.
그래서 방을 열지 않은 반 학생이 #student로 들어오면 다른 선생님이 연 방에 들어가고,
누가 새 작전을 열면 다른 반 작전이 통째로 바뀌었음.
(1) 작전을 열 때 숫자 4자리 작전 코드를 만들고 rooms/{코드}에 저장(24시간 안에 쓰인 코드는 피함).
(2) 지휘본부는 연 작전 코드를 이 기기(localStorage)에 기억 → 새로 고침·메인 갔다 와도 내 작전으로 돌아옴.
    다른 기기에서도 코드를 넣으면 같은 작전을 이어서 볼 수 있음.
(3) 학생 출동 링크·QR에 코드가 들어감(#student/1234). 코드 없이 #student로 오면 코드 입력 화면.
python3 tools/add_v38.py <in app-v37.html> <out app-v38.html>
"""
import sys
s=open(sys.argv[1],encoding='utf8').read()
def rep(o,n,c=1):
    global s;assert s.count(o)==c,(o[:70],s.count(o));s=s.replace(o,n)

# 상태: 지금 보고 있는 작전 코드와 방 문서 상태(loading/missing/ok)
rep("soloOn:(location.hash||'').slice(1)==='solo',solo:null,soloBack:null};",
    "soloOn:(location.hash||'').slice(1)==='solo',solo:null,soloBack:null,code:null,watching:undefined,roomState:'loading',roomUnsub:null};")

# 방 문서 경로: rooms/current → rooms/{코드}
rep("write('room',()=>S.db.doc('rooms/current').update({endAt:Date.now(),status:'ended'}))",
    "write('room',()=>roomDoc().update({endAt:Date.now(),status:'ended'}))")
rep("const roomRef=S.db.doc('rooms/current');","const roomRef=roomDoc();")
rep("write('room',()=>S.db.doc('rooms/current').update({status:'ended'}))","write('room',()=>roomDoc().update({status:'ended'}))")

# 방 구독: 코드가 바뀔 때마다 그 코드의 방 문서만 봄
rep("""  db.doc('rooms/current').onSnapshot(snap=>{const d=snap.exists?snap.data():null;const prev=S.room&&S.room.roomId;S.room=d;
    if((d&&d.roomId)!==prev){stop();S.local=null;S.jg=null;S.jc=null;subscribeRoomData(d&&d.roomId);S.prevPhase=null;}
    if(S.me&&d&&S.me.roomId!==d.roomId){S.me=null;ss('me',null);}
    render();},e=>{console.error(e);toast('실시간 연결이 끊겼어요. 페이지를 새로 고쳐 주세요.');});
}""","""  syncRoom();render();
}
// ---------- V38: 작전 코드(선생님·반마다 따로) ----------
const TCODE_KEY='goem-tcode';
function lsGet(k){try{return localStorage.getItem(k);}catch(e){return null;}}
function lsSet(k,v){try{if(v==null)localStorage.removeItem(k);else localStorage.setItem(k,v);}catch(e){}}
const okCode=v=>/^\\d{4}$/.test(String(v||''));
function roomDoc(code){return S.db.doc('rooms/'+(code||S.code));}
function hashCode(){const m=(location.hash||'').match(/^#student\\/(\\d{4})$/);return m?m[1]:null;}
function wantCode(){if(S.role==='teacher')return lsGet(TCODE_KEY);if(S.role==='student'){const h=hashCode();if(h)ss('code',h);return h||ss('code');}return null;}
function syncRoom(){if(!S.db)return;const c=wantCode();S.code=okCode(c)?String(c):null;if(S.code===S.watching)return;watchRoom(S.code);}
function watchRoom(code){if(S.roomUnsub){S.roomUnsub();S.roomUnsub=null;}S.watching=code;
  stop();S.room=null;S.local=null;S.jg=null;S.jc=null;S.prevPhase=null;subscribeRoomData(null);
  if(!code){S.roomState='missing';return;}
  S.roomState='loading';
  S.roomUnsub=roomDoc(code).onSnapshot(snap=>{if(S.watching!==code)return;const d=snap.exists?snap.data():null;const prev=S.room&&S.room.roomId;S.room=d;S.roomState=d?'ok':'missing';
    if((d&&d.roomId)!==prev){stop();S.local=null;S.jg=null;S.jc=null;subscribeRoomData(d&&d.roomId);S.prevPhase=null;}
    if(S.me&&d&&S.me.roomId!==d.roomId){S.me=null;ss('me',null);}
    render();},e=>{console.error(e);toast('실시간 연결이 끊겼어요. 페이지를 새로 고쳐 주세요.');});}
function setTeacherCode(code){lsSet(TCODE_KEY,code);syncRoom();}
function setStudentCode(code){ss('code',code);S.me=null;ss('me',null);
  if(code&&location.hash!=='#student/'+code){history.replaceState(null,'','#student/'+code);}
  else if(!code&&hashCode()){history.replaceState(null,'','#student');}
  syncRoom();S.key='';render();}
async function newCode(){for(let i=0;i<30;i++){const c=String(1000+Math.floor(Math.random()*9000));
    const snap=await roomDoc(c).get();const d=snap.exists?snap.data():null;
    if(!d||Date.now()-(d.createdAt||0)>24*3600e3)return c;}
  throw new Error('no free code');}
function codeForm(id,btnText,onGo){const inp=el('input',{type:'text',id,inputmode:'numeric',maxlength:'4',autocomplete:'off',placeholder:'0000',
    style:'width:120px;font-family:var(--f-mono);font-size:var(--t3);text-align:center;letter-spacing:.2em'});
  const go=()=>{const v=(inp.value||'').replace(/\\D/g,'');if(!okCode(v)){toast('숫자 4자리를 넣어 주세요.');inp.focus();return;}onGo(v);};
  inp.addEventListener('keydown',e=>{if(e.key==='Enter')go();});
  return el('div',{class:'row',style:'gap:10px'},inp,el('button',{type:'button',class:'btn-primary',onclick:go},btnText));}
function codeBadge(){return S.code?el('span',{class:'pill',style:'font-family:var(--f-mono)'},`작전 코드 ${S.code}`):'';}
function changeCodeBtn(){return el('button',{type:'button',class:'mini-btn',onclick:()=>setStudentCode(null)},'작전 코드 다시 넣기');}
function mountCode(app){app.append(el('div',{class:'title-screen'},bigLogo(),
  el('div',{class:'px panel stack',style:'max-width:560px;text-align:left'},el('h2',{},'작전 코드를 넣어 주세요'),
    el('p',{class:'muted'},'선생님 화면(지휘본부)에 보이는 숫자 4자리예요. 선생님이 준 링크나 QR로 들어오면 코드를 넣지 않아도 돼요.'),
    codeForm('scode','입장',v=>setStudentCode(v)),el('div',{},soloBtn()),roleSwitch())));
  setTimeout(()=>{const i=$('#scode');if(i)i.focus();},0);}""")

# 화면 고르기: 학생은 코드 없으면 코드 입력, 지휘본부는 내 작전이 없으면 개설 화면
rep("""  if(S.role==='teacher'){if(!r||S.tScreen==='setup')return 'tsetup';return `tdash|${r.roomId}`;}
  if(!r)return 'swait';""","""  if(S.role==='teacher'){if(!r||S.tScreen==='setup')return 'tsetup';return `tdash|${r.roomId}`;}
  if(!S.code)return 'scode';
  if(!r)return `swait|${S.code}|${S.roomState}`;""")
rep("tsetup:mountSetup,tdash:mountTeacher,swait:mountWait,","tsetup:mountSetup,tdash:mountTeacher,scode:mountCode,swait:mountWait,")

# 기다리는 화면: 코드에 맞는 작전이 없을 때 안내
rep("""function mountWait(app){app.append(el('div',{class:'title-screen'},bigLogo(),
  el('div',{class:'px panel stack',style:'max-width:560px;text-align:left'},el('h2',{},'지휘본부의 신호를 기다리는 중'),el('p',{class:'muted'},'선생님이 작전을 열면 이 화면이 자동으로 바뀌어요. 기다리는 동안 혼자 연습해도 좋아요.'),el('div',{},soloBtn()),roleSwitch())));}""",
"""function mountWait(app){const miss=S.roomState==='missing';app.append(el('div',{class:'title-screen'},bigLogo(),
  el('div',{class:'px panel stack',style:'max-width:560px;text-align:left'},el('h2',{},miss?`작전 코드 ${S.code}를 찾을 수 없어요`:'지휘본부에 연결하는 중'),
    el('p',{class:'muted'},miss?'코드를 다시 확인해 주세요. 선생님이 이 코드로 작전을 열면 이 화면이 자동으로 바뀌어요.':'잠시만 기다려 주세요.'),
    el('div',{class:'row'},soloBtn(),changeCodeBtn()),roleSwitch())));}""")

# 학생 선택 화면: 작전 코드 표시 + 코드 바꾸기
rep("""      el('p',{class:'notice'},`이번 작전: ${r.groupCount}모둠 · 모둠당 수호대원 ${r.channels}명 · ${r.bars}마디 · ${r.minutes}분`),
      el('div',{class:'row'},soloBtn('mini-btn'),roleSwitch())));""","""      el('p',{class:'notice'},`작전 코드 ${S.code} · 이번 작전: ${r.groupCount}모둠 · 모둠당 수호대원 ${r.channels}명 · ${r.bars}마디 · ${r.minutes}분`),
      el('div',{class:'row'},soloBtn('mini-btn'),changeCodeBtn(),roleSwitch())));""")

# 학생 출동 링크·QR: 코드 포함, 코드 크게
rep("""function studentLinkBox(){const inp=""","""function studentLinkBox(){const STUDENT_URL=STUDENT_BASE+'/'+S.code;const inp=""")
rep("""  return el('div',{class:'px panel stack',style:'gap:10px'},el('span',{class:'label'},'학생 출동 링크 · 학생 기기에서 이 주소로 열어요'),""",
"""  return el('div',{class:'px panel stack',style:'gap:10px'},
    el('div',{class:'row',style:'gap:12px;align-items:baseline'},el('span',{class:'label'},'작전 코드'),el('b',{style:'font-family:var(--f-mono);font-size:var(--t6);letter-spacing:.15em;color:var(--cyan)'},S.code),
      el('span',{style:'font-size:var(--t2);color:#d8d0ff'},'링크 없이 들어온 학생은 이 코드를 넣으면 돼요.')),
    el('span',{class:'label'},'학생 출동 링크 · 학생 기기에서 이 주소로 열어요'),""")
rep("const STUDENT_URL='https://claude.ai/artifact/GB58sEG5bWHmQf1Tmd2QRQ#student';",
    "const STUDENT_URL='https://claude.ai/artifact/GB58sEG5bWHmQf1Tmd2QRQ#student';const STUDENT_BASE=STUDENT_URL;")

# 작전 열기: 새 코드로 저장하고 이 기기에 기억
rep("""async function createRoom(st){stop();const roomId='r'+Date.now().toString(36);
  try{await S.db.doc('rooms/current').set({roomId,""","""async function createRoom(st){stop();const roomId='r'+Date.now().toString(36);
  try{const code=await newCode();await roomDoc(code).set({code,roomId,""")
rep("""    S.tScreen=null;S.afterRecruit='작전을 열었어요. 학생들에게 출동 링크를 나눠 주세요.';render();""",
    """    S.tScreen=null;setTeacherCode(code);S.afterRecruit=`작전을 열었어요. 작전 코드는 ${code}예요. 학생들에게 출동 링크나 코드를 나눠 주세요.`;render();""")
# 개설 화면: 다른 기기에서 연 작전 이어서 보기
rep("""        r?el('button',{type:'button',onclick:()=>{S.tScreen=null;render();}},'현재 작전으로 돌아가기'):'',roleSwitch())));}""",
"""        r?el('button',{type:'button',onclick:()=>{S.tScreen=null;render();}},'현재 작전으로 돌아가기'):'',roleSwitch())),
    el('div',{class:'px panel stack'},el('span',{class:'label'},'이미 연 작전 이어서 보기'),
      el('p',{class:'muted'},'다른 기기에서 연 작전이 있으면 그 작전 코드를 넣어 주세요.'),
      codeForm('tcode','이어서 보기',async v=>{try{const snap=await roomDoc(v).get();if(!snap.exists){toast(`작전 코드 ${v}를 찾을 수 없어요.`);return;}
        S.tScreen=null;setTeacherCode(v);render();}catch(e){console.error(e);toast('작전을 불러오지 못했어요. 다시 시도해 주세요.');}})));}""")
rep("""el('h1',{},'지휘본부')),
      el('div',{class:'timer-box px'}""","""el('h1',{},'지휘본부'),codeBadge()),
      el('div',{class:'timer-box px'}""")

# 라우팅: #student/1234 도 학생, 경로가 바뀌면 코드도 다시 맞춤
rep("if(h==='student'||h==='solo')return 'student';if(h==='teacher')return S.isOwner===false?'student':'teacher';",
    "if(h==='student'||h==='solo'||/^student\\/\\d{4}$/.test(h))return 'student';if(h==='teacher')return S.isOwner===false?'student':'teacher';")
rep("window.addEventListener('hashchange',()=>{stop();applyRoute();S.key='';render();});",
    "window.addEventListener('hashchange',()=>{stop();applyRoute();syncRoom();S.key='';render();});")
rep("function goHome(){stop();S.role=null;ss('role',null);S.tScreen=null;S.soloOn=false;",
    "function goHome(){stop();S.role=null;ss('role',null);S.tScreen=null;S.soloOn=false;S.watching=undefined;")
rep("function exitSolo(){stop();location.hash=S.soloBack!=null?S.soloBack:'student';}",
    "function exitSolo(){stop();location.hash=S.soloBack!=null?S.soloBack:(S.code?'student/'+S.code:'student');}")
open(sys.argv[2],'w',encoding='utf8').write(s);print('ok',len(s))
