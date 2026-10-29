async()=>{const B=window.__bs,out={};
 try{const before=B.S.bricks.find(b=>b.id===130);out.before=[before.px,before.py,before.pz];
  B.pickUp(130);await new Promise(r=>setTimeout(r,1500));B.place();await new Promise(r=>setTimeout(r,800));
  const a=B.S.bricks.find(b=>b.id===130);out.after=a?[a.px,a.py,a.pz]:null;out.n=B.S.bricks.length;out.bad=B.sel&&B.sel.bad;
 }catch(e){out.err=String(e)}
 return out}
