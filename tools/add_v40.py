"""V40: 지휘본부에서 모둠 작업 화면 실시간 보기
모둠 카드의 '작업 화면 보기'를 누르면 그 모둠의 채널(수호대원)별 음표 줄을 한 화면에 크게 보여 줌.
학생이 음표를 찍을 때마다 저장소 변경으로 바로 다시 그려짐(읽기 전용, 선생님이 고치지 않음).
이전·다음 모둠으로 넘겨 보기, 모둠 곡 재생·정지, Esc로 닫기.
python3 tools/add_v40.py <in app-v39.html> <out app-v40.html>
"""
import sys
s=open(sys.argv[1],encoding='utf8').read()
def rep(o,n,c=1):
    global s;assert s.count(o)==c,(o[:70],s.count(o));s=s.replace(o,n)

rep(".cards{display:grid;",""".mon{position:fixed;inset:0;z-index:19;background:rgba(11,8,32,.94);overflow:auto;padding:16px}
.mon>.panel{max-width:1240px;margin:0 auto}
.mon-lanes{overflow-x:auto;display:flex;flex-direction:column;gap:6px;padding-bottom:6px}
.mon-row{display:flex;align-items:stretch;gap:0;min-width:max-content}
.mon-lab{position:sticky;left:0;z-index:1;flex:none;width:168px;padding:6px 8px;background:#0b0820;display:flex;flex-direction:column;justify-content:center;gap:2px;font-size:var(--t2);border-right:2px solid #4a3c9c}
.mon-lab b{font-size:var(--t3)}
.cards{display:grid;""")

# 카드에 '작업 화면 보기'
rep("""playing?'■ 정지':'▶ 모둠 곡 재생'),
        ph==='running'?""","""playing?'■ 정지':'▶ 모둠 곡 재생'),
        el('button',{type:'button',class:'mini-btn',onclick:()=>openMon(g)},'🔍 작업 화면 보기'),
        ph==='running'?""")
rep("""        ph==='running'?(gDone?el('button',{type:'button',class:'mini-btn',onclick:()=>write('g'+g,()=>ref.update({done:false}))},'이 모둠 다시 열기'):confirmBtn('이 모둠 창작 종료','한 번 더 누르면 종료',()=>endGroup(g),'mini-btn')):'')));});
  tickTimer();}""","""        ph==='running'?(gDone?el('button',{type:'button',class:'mini-btn',onclick:()=>write('g'+g,()=>ref.update({done:false}))},'이 모둠 다시 열기'):confirmBtn('이 모둠 창작 종료','한 번 더 누르면 종료',()=>endGroup(g),'mini-btn')):'')));});
  tickTimer();monDraw();}
// ---------- V40: 모둠 작업 화면 실시간 보기(지휘본부, 읽기 전용) ----------
function openMon(g){S.mon=g;monDraw();}
function closeMon(){S.mon=null;const m=$('#mon');if(m)m.remove();}
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&S.mon)closeMon();});
function monDraw(){const r=S.room,g=S.mon;let ov=$('#mon');
  if(!g||!r||S.key.split('|')[0]!=='tdash'||g>r.groupCount){if(ov)ov.remove();if(g)S.mon=null;return;}
  const keepTop=ov?ov.scrollTop:0,lanes0=ov&&ov.querySelector('.mon-lanes'),keepLeft=lanes0?lanes0.scrollLeft:0;
  if(!ov){ov=el('div',{class:'mon',id:'mon',role:'dialog','aria-label':`${g}모둠 작업 화면`});document.body.append(ov);}
  const ph=phase(),grp=S.groups[gid(r.roomId,g)]||{g,chords:[]},seats=gList(r,g);
  const chords=grp.chords&&grp.chords.length?grp.chords:Array(r.bars).fill(null);
  const playing=S.tPlay===g&&A.timer,gDone=ph==='running'&&grp.done;
  let total=0;const lanes=el('div',{class:'mon-lanes'});
  for(const c of seats){const t=S.tracks[tid(r.roomId,g,c)]||null,inst=instOf(c,t),set=toSet(t&&t.notes),nr=rowsOf(inst);total+=set.size;
    const cv=el('canvas',{});
    lanes.append(el('div',{class:'mon-row'},
      el('div',{class:'mon-lab'},el('b',{style:`color:${chColor(c)}`},(grp.leader===c?'★ ':'')+hero(c).name),
        el('span',{},t&&t.name?t.name:'빈자리'),el('span',{class:'muted'},`${INSTS[inst]||inst} · 음표 ${set.size}`)),cv));
    drawLane(cv,set,chColor(c),Math.max(10,Math.round(84/nr)),{chords:inst==='drum'?null:chords,drum:inst==='drum',inst});}
  const nav=d=>{const n=g+d;if(n>=1&&n<=r.groupCount){S.mon=n;const l=$('#mon .mon-lanes');if(l)l.scrollLeft=0;monDraw();}};
  ov.replaceChildren(el('div',{class:'px panel stack'},
    el('div',{class:'row',style:'justify-content:space-between;align-items:center'},
      el('div',{class:'row',style:'gap:10px;align-items:baseline'},el('h2',{},`${g}모둠 작업 화면`),
        el('span',{class:'pill '+(gDone?'ok':ph==='running'?'run':'')},gDone?'창작 종료':PHASE_TXT[ph]||''),el('span',{class:'mono',style:'color:var(--cyan)'},`NOTES ${total}`),
        el('span',{class:'muted'},'실시간 · 보기만 해요')),
      el('div',{class:'row'},
        el('button',{type:'button',class:'mini-btn',disabled:g<=1,onclick:()=>nav(-1)},'◀ 이전 모둠'),
        el('button',{type:'button',class:'mini-btn',disabled:g>=r.groupCount,onclick:()=>nav(1)},'다음 모둠 ▶'),
        el('button',{type:'button','data-nosfx':'1',class:playing?'btn-primary':'',onclick:()=>{if(playing){stop();updateTeacher();return;}stop();S.tPlay=g;play();updateTeacher();}},playing?'■ 정지':'▶ 모둠 곡 재생'),
        el('button',{type:'button',onclick:closeMon},'✕ 닫기'))),
    el('div',{class:'row',style:'gap:10px;align-items:center'},el('span',{class:'label'},`코드 진행 · BPM ${grp.bpm||90}`),
      el('div',{class:'chips'},chords.map(ch=>el('span',{class:'chip'+(ch?'':' empty')},ch||'?')))),
    lanes));
  lanes.scrollLeft=keepLeft;ov.scrollTop=keepTop;}""")
rep("const v=S.key.split('|')[0];if(v==='tdash')updateTeacher();","const v=S.key.split('|')[0];if(v==='tdash')updateTeacher();else if(S.mon)closeMon();")
open(sys.argv[2],'w',encoding='utf8').write(s);print('ok',len(s))
