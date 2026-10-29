async()=>{const B=window.__bs,out={},T=THREE;const m=B.meshes.get(1);m.updateMatrixWorld(true);const bb=new T.Box3().setFromObject(m);out.bb=[bb.min.toArray(),bb.max.toArray()];
  B.selectPart('ld:2780');await new Promise(r=>setTimeout(r,4000));B.selectPart('ld:2780');
  const c=bb.getCenter(new T.Vector3());const p=new T.Vector3(c.x+1,c.y,bb.max.z);
  B.tapBuild({cell:{x:Math.floor(p.x),z:Math.floor(p.z)},bid:1,mesh:m,point:p});const pos=()=>{const x=B.snapXf(B.sel);return x.pos.toArray().map(v=>+v.toFixed(2))};
  out.tap=p.toArray();out.first=pos();out.tl=B.sel.Tl&&B.sel.Tl.length;out.C=B.sel.C.length;out.steps=[];
  for(let i=0;i<4;i++){document.querySelector('#nextHole').click();out.steps.push(pos())}return out}
