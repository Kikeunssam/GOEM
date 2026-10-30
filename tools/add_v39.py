"""V39: 학생 기기 잠금 + 선생님 번호
(1) 학생이 작전 코드로 작전에 들어오면 그 기기를 '학생 기기'로 잠금(localStorage, 8시간).
    잠긴 기기에서는 뒤로가기·메인화면으로·#teacher 주소가 모두 학생 화면으로 돌아감(출동 모드·지휘본부 못 감).
    작전을 연 기기(지휘본부 기기)는 잠기지 않음 → 선생님이 '새 탭에서 학생 화면 열기'로 확인해도 괜찮음.
(2) 작전을 열 때 선생님 번호(숫자 4자리)를 함께 만듦. 지휘본부 '선생님 번호 보기'를 눌러야 보임.
    다른 기기에서 '이미 연 작전 이어서 보기'를 하려면 작전 코드 + 선생님 번호가 필요함
    → 학생이 작전 코드를 알아도 선생님 작전을 조종할 수 없음.
    잠긴 기기도 코드 화면의 '선생님이세요?'에서 작전 코드 + 선생님 번호를 넣으면 풀림.
(3) V38 버그: 학생 링크가 #student/코드가 되면서 연습 모드에 '출동 화면으로'가 안 나오고 '메인화면으로'가 나오던 것 고침.
python3 tools/add_v39.py <in app-v38.html> <out app-v39.html>
"""
import sys
s=open(sys.argv[1],encoding='utf8').read()
def rep(o,n,c=1):
    global s;assert s.count(o)==c,(o[:70],s.count(o));s=s.replace(o,n)

# (3) 연습 모드에서 학생 화면으로 돌아가기
rep("(v==='solo'&&S.soloBack!=='student')","(v==='solo'&&!fromStudent())")
rep("S.soloBack==='student'?el('button',{type:'button',onclick:exitSolo},'← 출동 화면으로'):''","fromStudent()?el('button',{type:'button',onclick:exitSolo},'← 출동 화면으로'):''")

# (1) 잠금 도우미 + (2) 선생님 번호 폼
rep("function setTeacherCode(code){lsSet(TCODE_KEY,code);syncRoom();}",
"""function setTeacherCode(code){lsSet(TCODE_KEY,code);if(code)markTeacherDev();syncRoom();}
// ---------- V39: 학생 기기 잠금 · 선생님 번호 ----------
const SLOCK_KEY='goem-slock',TDEV_KEY='goem-teacher',SLOCK_MS=8*3600e3;
function isTeacherDev(){return !!(lsGet(TDEV_KEY)||lsGet(TCODE_KEY));}
function markTeacherDev(){lsSet(TDEV_KEY,'1');lsSet(SLOCK_KEY,null);}
function stuLocked(){if(isTeacherDev())return false;const t=+(lsGet(SLOCK_KEY)||0);return !!t&&Date.now()-t<SLOCK_MS;}
function lockStudent(){if(!isTeacherDev())lsSet(SLOCK_KEY,String(Date.now()));}
function fromStudent(){return S.soloBack!=null?/^student(\\/|$)/.test(S.soloBack):stuLocked();}
function stuHash(){const c=S.code||ss('code');return okCode(c)?'student/'+c:'student';}
function newKey(){return String(1000+Math.floor(Math.random()*9000));}
// 작전 코드 + 선생님 번호 → 그 작전의 지휘본부로
function teacherResumeForm(after){const ci=el('input',{type:'text',inputmode:'numeric',maxlength:'4',autocomplete:'off',placeholder:'작전 코드',style:'width:130px;font-family:var(--f-mono);font-size:var(--t4);text-align:center'});
  const ki=el('input',{type:'password',inputmode:'numeric',maxlength:'4',autocomplete:'off',placeholder:'선생님 번호',style:'width:130px;font-family:var(--f-mono);font-size:var(--t4);text-align:center'});
  const go=async()=>{const c=(ci.value||'').replace(/\\D/g,''),k=(ki.value||'').replace(/\\D/g,'');
    if(!okCode(c)){toast('작전 코드 숫자 4자리를 넣어 주세요.');ci.focus();return;}
    try{const snap=await roomDoc(c).get();const d=snap.exists?snap.data():null;
      if(!d){toast(`작전 코드 ${c}를 찾을 수 없어요.`);return;}
      if(d.tkey&&d.tkey!==k){toast('선생님 번호가 맞지 않아요.');ki.value='';ki.focus();return;}
      S.tScreen=null;markTeacherDev();setTeacherCode(c);if(after)after();else render();}
    catch(e){console.error(e);toast('작전을 불러오지 못했어요. 다시 시도해 주세요.');}};
  [ci,ki].forEach(i=>i.addEventListener('keydown',e=>{if(e.key==='Enter')go();}));
  return el('div',{class:'row',style:'gap:10px'},ci,ki,el('button',{type:'button',class:'btn-primary',onclick:go},'지휘본부로'));}
function teacherUnlock(){const box=el('div',{class:'stack',style:'gap:8px'});
  const btn=el('button',{type:'button',class:'mini-btn',onclick:()=>{btn.remove();box.append(el('p',{class:'muted'},'지휘본부 화면 위쪽의 ‘선생님 번호 보기’에 나오는 번호예요.'),
    teacherResumeForm(()=>{S.me=null;ss('me',null);ss('code',null);location.hash='teacher';}));}},'선생님이세요?');
  box.append(btn);return box;}""")

# 학생이 작전에 들어오면 잠금
rep("""S.room=d;S.roomState=d?'ok':'missing';""","""S.room=d;S.roomState=d?'ok':'missing';if(d&&S.role==='student')lockStudent();""")

# 라우팅: 잠긴 기기는 메인·지휘본부 대신 학생 화면
rep("function routeRole(){const h=(location.hash||'').slice(1);",
    "function routeRole(){const h=(location.hash||'').slice(1);if(stuLocked()&&h!=='solo'&&!/^student(\\/\\d{4})?$/.test(h))return 'student';")
rep("function applyRoute(){S.soloOn=(location.hash||'').slice(1)==='solo';",
    "function applyRoute(){{const h=(location.hash||'').slice(1);if(stuLocked()&&h!=='solo'&&!/^student(\\/\\d{4})?$/.test(h))history.replaceState(null,'','#'+stuHash());}S.soloOn=(location.hash||'').slice(1)==='solo';")
rep("function goHome(){stop();",
    "function goHome(){if(stuLocked()){stop();S.soloOn=false;location.hash=stuHash();return;}stop();")

# 코드 입력 화면: 선생님 잠금 풀기
rep("codeForm('scode','입장',v=>setStudentCode(v)),el('div',{},soloBtn()),roleSwitch())));",
    "codeForm('scode','입장',v=>setStudentCode(v)),el('div',{},soloBtn()),roleSwitch(),teacherUnlock())));")

# (2) 작전 열 때 선생님 번호, 지휘본부에서 보기, 이어서 보기에 번호 필요
rep("await roomDoc(code).set({code,roomId,","await roomDoc(code).set({code,tkey:newKey(),roomId,")
rep("""      el('p',{class:'muted'},'다른 기기에서 연 작전이 있으면 그 작전 코드를 넣어 주세요.'),
      codeForm('tcode','이어서 보기',async v=>{try{const snap=await roomDoc(v).get();if(!snap.exists){toast(`작전 코드 ${v}를 찾을 수 없어요.`);return;}
        S.tScreen=null;setTeacherCode(v);render();}catch(e){console.error(e);toast('작전을 불러오지 못했어요. 다시 시도해 주세요.');}})));}""",
"""      el('p',{class:'muted'},'다른 기기에서 연 작전이 있으면 작전 코드와 선생님 번호를 넣어 주세요. 선생님 번호는 그 기기의 지휘본부에서 ‘선생님 번호 보기’를 누르면 보여요.'),
      teacherResumeForm()));}""")
rep("el('div',{class:'row'},el('button',{type:'button',onclick:()=>{S.tScreen='setup';render();}},'새 작전 열기'),roleSwitch()));}",
    "el('div',{class:'row'},el('button',{type:'button',onclick:()=>{S.tScreen='setup';render();}},'새 작전 열기'),tkeyBtn(),roleSwitch()));}\n"
    "function tkeyBtn(){const b=el('button',{type:'button',class:'mini-btn',onclick:()=>{const k=S.room&&S.room.tkey;b.textContent=b.dataset.on?'선생님 번호 보기':(k?`선생님 번호 ${k} · 숨기기`:'이 작전은 선생님 번호가 없어요');if(b.dataset.on)delete b.dataset.on;else b.dataset.on='1';}},'선생님 번호 보기');\n"
    "  b.title='다른 기기에서 이 작전을 이어 볼 때 필요해요. 학생에게는 알려 주지 마세요.';return b;}")
open(sys.argv[2],'w',encoding='utf8').write(s);print('ok',len(s))
