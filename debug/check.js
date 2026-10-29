()=>{const B=window.__bs,out={ov:[],desc:{}};const bb=id=>{const m=B.meshes.get(id),g=B.info(B.brickById(id).p);m.updateMatrixWorld(true);return (g.body||g.geo).boundingBox.clone().applyMatrix4(m.matrixWorld)};
  const L=B.S.bricks.map(b=>({b,x:bb(b.id)})),vol=x=>Math.max(0,x.max.x-x.min.x)*Math.max(0,x.max.y-x.min.y)*Math.max(0,x.max.z-x.min.z);
  for(let i=0;i<L.length;i++)for(let j=i+1;j<L.length;j++){const a=L[i].x.clone(),c=L[j].x.clone();a.expandByScalar(-.08);c.expandByScalar(-.08);if(!a.intersectsBox(c))continue;
    const r=vol(a.clone().intersect(c))/Math.min(vol(a),vol(c));if(r>.15)out.ov.push([L[i].b.id,L[i].b.p,L[i].b.c,L[j].b.id,L[j].b.p,L[j].b.c,+r.toFixed(2)])}
  return out}
