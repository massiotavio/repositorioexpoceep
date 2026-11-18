
/* =====================================================================
   CAMADA DE ANIMAÇÕES (adicionada) — só "envolve" as funções do jogo;
   a lógica dos enigmas e as chamadas à API continuam intactas.
   ===================================================================== */
(function animations(){
const RM=false;
const $=id=>document.getElementById(id),app=$('app'),main=document.querySelector('main');
const restart=(el,cls,ms=1000)=>{if(!el)return;el.classList.remove(cls);void el.offsetWidth;el.classList.add(cls);setTimeout(()=>el.classList.remove(cls),ms)};
const R=(a,b)=>a+Math.random()*(b-a);

/* ---------- 1. transição entre telas (tela antiga sai como "fantasma") ---------- */
const _go=window.go;let cur=0;
window.go=function(n){
  const old=document.querySelector('.screen.active'),back=n<cur;
  app.dataset.dir=back?'b':'f';
  if(!RM&&old&&old.id!=='s'+n){
    const g=old.cloneNode(true);
    g.querySelectorAll('[id]').forEach(e=>e.removeAttribute('id'));g.removeAttribute('id');
    g.className='screen ghost';g.setAttribute('aria-hidden','true');
    g.style.cssText=`top:${old.offsetTop}px;left:${old.offsetLeft}px;width:${old.offsetWidth}px`;
    main.appendChild(g);setTimeout(()=>g.remove(),340);
  }
  const prevDone=[...document.querySelectorAll('#progress span.done')].length;
  const r=_go.apply(this,arguments);cur=n;
  /* segmento de progresso recém-conquistado "estoura" */
  document.querySelectorAll('#progress span').forEach((s,i)=>{if(i>=prevDone&&s.classList.contains('done'))restart(s,'just',1000)});
  /* textos da tela digitados na primeira visita */
  const scr=$('s'+n);if(scr)scr.querySelectorAll('.prompt,.lead').forEach(typeIn);
  /* tela final: contagem do tempo + confete */
  if(n===7&&!RM){setTimeout(countTime,650);setTimeout(()=>confetti(),500);setTimeout(()=>confetti(),1500)}
  return r;
};

/* ---------- 2. efeito máquina de escrever (preserva <br> e <span>) ---------- */
function typeIn(el){
  if(RM||el._typed)return;el._typed=true;
  const w=document.createTreeWalker(el,NodeFilter.SHOW_TEXT),nodes=[];
  for(let n;n=w.nextNode();)if(n.nodeValue.trim())nodes.push([n,n.nodeValue]);
  const total=nodes.reduce((a,x)=>a+x[1].length,0);if(!total)return;
  nodes.forEach(x=>x[0].nodeValue='');el.classList.add('typing');
  const per=Math.max(1,Math.ceil(total/90)); /* ~1,5 s no máximo */
  let shown=0;const step=()=>{
    shown=Math.min(total,shown+per);let left=shown;
    nodes.forEach(([n,t])=>{const k=Math.max(0,Math.min(t.length,left));n.nodeValue=t.slice(0,k);left-=t.length});
    if(shown<total)setTimeout(step,16);else el.classList.remove('typing');
  };setTimeout(step,260);
}
document.querySelectorAll('#s0 .prompt,#s0 .lead').forEach(typeIn);

/* ---------- 3. feedback de acerto / erro ---------- */
const _setFeedback=window.setFeedback;
window.setFeedback=function(id,msg,cls){
  _setFeedback.apply(this,arguments);
  const e=$(id);if(e&&/good|bad/.test(cls||'')){e.style.animation='none';void e.offsetWidth;e.style.animation=''}
};
const hit=(id,cls)=>{const e=$(id);if(!e)return;const p=e.closest('.panel');if(p)restart(p,cls,950);else if(cls==='flash-bad'){const h=e.closest('.hero');if(h)restart(h,'flash-shake',600)}};
const _good=window.good,_bad=window.bad;
window.good=function(id){hit(id,'flash-ok');return _good.apply(this,arguments)};
window.bad=function(id){hit(id,'flash-bad');return _bad.apply(this,arguments)};

/* ---------- 4. enigma 01: símbolo novo "estoura" no slot ---------- */
const _renderSymbols=window.renderSymbols;let prevSyms=0;
window.renderSymbols=function(){
  _renderSymbols.apply(this,arguments);
  if(symbolSeq.length>prevSyms){const s=document.querySelectorAll('#slots .slot')[symbolSeq.length-1];if(s)restart(s,'pop',700)}
  prevSyms=symbolSeq.length;
};

/* ---------- 5. enigma 02: módulo ativado + números que pulsam ---------- */
const _renderCircuit=window.renderCircuit;let prevNodes=0;
window.renderCircuit=function(){
  _renderCircuit.apply(this,arguments);
  if(circuitSeq.length>prevNodes){const n=document.querySelectorAll('#circuit .node')[circuitSeq[circuitSeq.length-1]];if(n)restart(n,'just',900)}
  if(circuitSeq.length!==prevNodes){restart($('energy'),'bump',600);restart($('circuitStatus'),'bump',600)}
  prevNodes=circuitSeq.length;
};

/* ---------- 6. enigma 03: display do código ---------- */
const _renderCode=window.renderCode;let prevLen=0;
window.renderCode=function(){_renderCode.apply(this,arguments);if(code.length!==prevLen)restart($('codeDisplay'),'tick',400);prevLen=code.length};

/* ---------- 7. enigma 04: linha de varredura sobre o binário ---------- */
const bin=document.querySelector('#s4 .binary');if(bin&&!RM){const l=document.createElement('i');l.className='scanline';bin.appendChild(l)}

/* ---------- 8. enigma 05: disco do cadeado "vira" ---------- */
const _turnDial=window.turnDial;
window.turnDial=function(i,dir){
  _turnDial.apply(this,arguments);
  const d=document.querySelectorAll('#dials .digit')[i];if(d)restart(d,dir>0?'flipU':'flipD',400);
};

/* ---------- 9. tempo final: contagem de 00:00 até o valor ---------- */
function countTime(){
  const el=$('endTime');if(!el)return;const m=/^(\d\d):(\d\d)$/.exec(el.textContent.trim());if(!m)return;
  const total=+m[1]*60+ +m[2],t0=performance.now(),dur=1400;el.classList.add('counting');
  const f=now=>{const k=Math.min(1,(now-t0)/dur),v=Math.round(total*(1-Math.pow(1-k,3)));el.textContent=fmtTempo(v);
    if(k<1)requestAnimationFrame(f);else{el.textContent=fmtTempo(total);el.classList.remove('counting')}};
  requestAnimationFrame(f);
}

/* ---------- 10. confete pixelado na tela final ---------- */
let cv,cx,parts=[],raf=0;
function confetti(){
  if(RM)return;
  if(!cv){cv=document.createElement('canvas');cv.id='confetti';app.appendChild(cv);cx=cv.getContext('2d')}
  const dpr=Math.min(devicePixelRatio||1,2),W=innerWidth,H=innerHeight;cv.width=W*dpr;cv.height=H*dpr;cx.setTransform(dpr,0,0,dpr,0,0);
  const cols=['#00d9f5','#43f5a2','#a678ff','#ffc45c','#c8ff6a','#ffffff'];
  [[0,.9],[W,-.9]].forEach(([x0,dir])=>{for(let i=0;i<70;i++){const v=R(520,1050);
    parts.push({x:x0,y:H*.85,vx:(dir>0?1:-1)*Math.cos(R(.45,1.25))*v,vy:-Math.sin(R(.45,1.25))*v,s:Math.round(R(4,9)),c:cols[Math.random()*cols.length|0],life:R(2.2,3.6),age:0,spin:R(-8,8),rot:R(0,6)})}});
  if(!raf){let last=performance.now();const loop=now=>{const dt=Math.min(.05,(now-last)/1000);last=now;cx.clearRect(0,0,W,H);
    parts=parts.filter(p=>(p.age+=dt)<p.life);
    parts.forEach(p=>{p.vy+=900*dt;p.vx*=.992;p.x+=p.vx*dt;p.y+=p.vy*dt;p.rot+=p.spin*dt;
      cx.save();cx.globalAlpha=Math.min(1,(p.life-p.age)*1.5);cx.translate(p.x,p.y);cx.rotate(p.rot);cx.fillStyle=p.c;cx.fillRect(-p.s/2,-p.s/2,p.s,p.s*(.5+.5*Math.abs(Math.cos(p.age*6))));cx.restore()});
    if(parts.length)raf=requestAnimationFrame(loop);else{raf=0;cx.clearRect(0,0,W,H)}};
    raf=requestAnimationFrame(loop)}
}

/* ---------- 11. foco de luz que segue o mouse ---------- */
if(!RM){
  const spot=document.createElement('div');spot.className='spot';app.appendChild(spot);let q=false,mx=0,my=0;
  addEventListener('pointermove',e=>{if(e.pointerType!=='mouse')return;mx=e.pageX;my=e.pageY;if(q)return;q=true;
    requestAnimationFrame(()=>{q=false;spot.style.setProperty('--mx',mx+'px');spot.style.setProperty('--my',my+'px');spot.classList.add('on')})});
  document.addEventListener('mouseleave',()=>spot.classList.remove('on'));
}
})();
