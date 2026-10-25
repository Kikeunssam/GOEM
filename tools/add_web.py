"""claude.ai 아티팩트판(app-vNN.html) → 깃허브 페이지판(index.html).
실시간 저장소: claude.ai db → Firebase Firestore(compat SDK). 모두 익명 로그인. 지휘본부는 잠금 없이 누구나(#teacher).
python3 tools/add_web.py <app-vNN.html> <index.html>
"""
import sys
s=open(sys.argv[1],encoding='utf8').read()
def rep(o,n,c=1):
    global s;assert s.count(o)==c,(o[:80],s.count(o));s=s.replace(o,n)

FB='10.14.1'
head=''.join(f'<script src="https://www.gstatic.com/firebasejs/{FB}/firebase-{m}-compat.js"></script>\n' for m in ('app','auth','firestore'))
head+='<script src="firebase-config.js"></script>\n'
rep('<script>',head+'<script>')

# 학생 링크: 지금 주소 기준
rep("const STUDENT_URL='https://claude.ai/artifact/GB58sEG5bWHmQf1Tmd2QRQ#student';",
    "const STUDENT_URL=location.origin+location.pathname+'#student';")

# 연결 안 될 때 안내
rep("이 화면에서는 작전 본부(실시간 저장소)에 연결할 수 없어요. claude.ai에 로그인한 상태로 이 링크를 다시 열어 주세요.",
    "작전 본부(실시간 저장소)에 연결할 수 없어요. 인터넷 연결을 확인하고 페이지를 새로 고쳐 주세요.")
rep("toast('입장하지 못했어요. 선생님께 편집 권한이 있는지 물어봐 주세요.')","toast('입장하지 못했어요. 인터넷 연결을 확인하고 다시 눌러 주세요.')")

# 선착순 자리 잡기: 잠금(acquire) 대신 Firestore 트랜잭션
rep("""    const lease=await ref.acquire({holder:DEV,ttlMs:4000});
    if(!lease.acquired){lost();return;}
    const snap=await ref.get();const d=snap.exists?snap.data():null;
    if(takenBy(d)){lost();return;}
    if(d&&d.inst){await ref.update({name,owner:DEV});S.local={inst:d.inst,oct:d.oct,notes:toSet(d.notes)};}
    else{const inst=DEFAULT_INST[(c-1)%6];await ref.set({roomId:r.roomId,g,c,name,owner:DEV,inst,oct:INST_OCT[inst],notes:[],updatedAt:Date.now()});S.local={inst,oct:INST_OCT[inst],notes:new Map()};}
""","""    const got=await S.db.runTransaction(async tx=>{const snap=await tx.get(ref);const d=snap.exists?snap.data():null;
      if(takenBy(d))return null;
      if(d&&d.inst){tx.update(ref,{name,owner:DEV});return {inst:d.inst,oct:d.oct,notes:d.notes};}
      const inst=DEFAULT_INST[(c-1)%6];tx.set(ref,{roomId:r.roomId,g,c,name,owner:DEV,inst,oct:INST_OCT[inst],notes:[],updatedAt:Date.now()});return {inst,oct:INST_OCT[inst],notes:[]};});
    if(!got){lost();return;}
    S.local={inst:got.inst,oct:got.oct,notes:toSet(got.notes)};
""")

# 지휘본부: 잠금 없음(사용자 결정). 누구나 #teacher로 열 수 있음

rep("function routeRole(){const h=(location.hash||'').slice(1);if(h==='student'||h==='solo')return 'student';if(h==='teacher')return S.isOwner===false?'student':'teacher';return null;}",
    "function routeRole(){const h=(location.hash||'').slice(1);if(h==='student'||h==='solo')return 'student';if(h==='teacher')return 'teacher';return null;}")
rep("S.role=r||ss('role');if(S.role==='teacher'&&S.isOwner===false)S.role=null;","S.role=r||ss('role');")
rep("const teacherOk=S.isOwner!==false;","const teacherOk=true;")

# 부팅: Firebase 연결 + 익명 로그인
rep("""  let db=null;try{db=await window.claude.use('db');}catch(e){db=null;}
  S.db=db;
  try{const u=await window.claude.use('user');S.isOwner=u?await u.isOwner():null;}catch(e){S.isOwner=null;}
""","""  let db=null;
  try{firebase.initializeApp(window.GOEM_FIREBASE);S.auth=firebase.auth();db=firebase.firestore();
    await new Promise(res=>{const un=S.auth.onAuthStateChanged(()=>{un();res();});});
    if(!S.auth.currentUser)await S.auth.signInAnonymously();
    S.db=db;S.isOwner=true;}
  catch(e){console.error(e);db=null;S.db=null;}
""")
rep("if(window.claude&&window.claude.use)boot();else{S.db=null;render();}",
    "if(window.firebase&&window.GOEM_FIREBASE&&window.GOEM_FIREBASE.apiKey)boot();else{S.db=null;applyRoute();render();}")
open(sys.argv[2],'w',encoding='utf8').write(s);print('ok',len(s))
