"""V37: 학생 활동 모드 리더 기능
(1) 작전 회의(로비)에서 리더도 '코드 진행 추천'을 누를 수 있음(연습실과 같은 추천 목록, 8마디면 4마디 진행을 두 번).
(2) 출동(작전 중)에도 리더가 재생 줄의 빠르기 막대로 BPM을 바꿀 수 있음. 모둠 문서(groups.bpm)에 저장돼 모둠원 모두에게 바로 반영되고,
    다른 모둠원에게는 '리더가 빠르기를 바꿨어요' 알림이 뜸.
python3 tools/add_v37.py <in app-v36.html> <out app-v37.html>
"""
import sys
s=open(sys.argv[1],encoding='utf8').read()
def rep(o,n,c=1):
    global s;assert s.count(o)==c,(o[:70],s.count(o));s=s.replace(o,n)

# (1) 로비: 리더 '코드 진행 추천'
rep("""    const row=el('div',{class:'row'});
    if(r.bars===8)row.append(""","""    const row=el('div',{class:'row'});
    row.append(el('button',{type:'button',onclick:()=>{const p=SOLO_PROGS[Math.floor(Math.random()*SOLO_PROGS.length)];const nc=Array.from({length:r.bars},(_,i)=>p[i%4]);save({chords:nc,ready:false});toast('코드 진행을 새로 뽑았어요: '+p.join(' - '));}},'코드 진행 추천'));
    if(r.bars===8)row.append(""")

# (2) 작전 중: 리더 BPM 막대(재생 줄)
rep("""      el('span',{class:'mono',id:'bpmInfo',style:'color:var(--cyan)'},''),lenSeg()),
    el('div',{id:'lockmsg'}),""","""      el('span',{class:'mono',id:'bpmInfo',style:'color:var(--cyan)'},''),liveBpm(),lenSeg()),
    el('div',{id:'lockmsg'}),""")
rep("""function updateDaw(){const r=S.room,me=S.me;if(!r||!me||!$('#heads'))return;const grp=myGroup()||{};const ph=phase();""",
"""// 작전 중 리더 빠르기 막대: 모둠 문서에 저장 → 모둠원 재생에 바로 반영
function liveBpm(){const rng=el('input',{type:'range',id:'bpmLive',min:'60',max:'140',step:'5',value:'90','aria-label':'빠르기(리더)',title:'리더만 바꿀 수 있어요'});
  const box=el('span',{class:'row',id:'bpmLiveBox',style:'gap:6px;display:none'},el('span',{class:'label'},'빠르기'),rng);
  rng.addEventListener('pointerdown',()=>{S.bpmDrag=true;});
  rng.addEventListener('input',()=>{S.bpmDrag=true;$('#bpmInfo').textContent=`BPM ${rng.value}`;});
  rng.addEventListener('change',()=>{S.bpmDrag=false;const r=S.room,me=S.me,gp=r&&me&&myGroup();if(!gp||gp.leader!==me.c)return;const v=+rng.value;
    S.bpmSeen=v;write('grp',()=>S.db.collection('groups').doc(gid(r.roomId,me.g)).update({bpm:v}));});
  return box;}
function updateLiveBpm(grp,ph){const box=$('#bpmLiveBox'),rng=$('#bpmLive');if(!box||!rng)return;const me=S.me,bpm=grp.bpm||90;
  box.style.display=ph==='running'&&grp.leader===me.c?'flex':'none';
  if(!S.bpmDrag&&document.activeElement!==rng)rng.value=String(bpm);
  if(ph==='running'&&S.bpmSeen!=null&&S.bpmSeen!==bpm&&grp.leader!==me.c)toast(`리더가 빠르기를 BPM ${bpm}(으)로 바꿨어요.`);
  S.bpmSeen=bpm;}
function updateDaw(){const r=S.room,me=S.me;if(!r||!me||!$('#heads'))return;const grp=myGroup()||{};const ph=phase();""")
rep("""  $('#bpmInfo').textContent=`BPM ${grp.bpm||90}`;
  for(const c of gList(r,me.g))""","""  if(!S.bpmDrag)$('#bpmInfo').textContent=`BPM ${grp.bpm||90}`;updateLiveBpm(grp,ph);
  for(const c of gList(r,me.g))""")
open(sys.argv[2],'w',encoding='utf8').write(s);print('ok',len(s))
