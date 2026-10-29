()=>{const B=window.__bs,out={gaps:[],names:{}};const bb=id=>{const m=B.meshes.get(id),g=B.info(B.brickById(id).p);m.updateMatrixWorld(true);return (g.body||g.geo).boundingBox.clone().applyMatrix4(m.matrixWorld)};
  const L=B.S.bricks.map(b=>({b,x:bb(b.id)}));
  for(const b of B.S.bricks){out.names[b.p]=(B.info(b.p).name||'')}
  for(let i=0;i<L.length;i++)for(let j=i+1;j<L.length;j++){const a=L[i].x,c=L[j].x;
    const ov=k=>Math.min(a.max[k],c.max[k])-Math.max(a.min[k],c.min[k]);
    for(const k of ['x','y','z']){const o=['x','y','z'].filter(q=>q!==k);if(ov(o[0])<.3||ov(o[1])<.3)continue;const g=-ov(k);if(g>.02&&g<.35)out.gaps.push([L[i].b.id,L[i].b.p,L[j].b.id,L[j].b.p,k,+g.toFixed(3)])}}
  return out}
