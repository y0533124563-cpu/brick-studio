()=>{const B=window.__bs,T=THREE,out={};const b=B.brickById(61),m=B.meshes.get(61);
  B.selectPart(b.p);const q=new T.Quaternion(...b.q);
  for(const dx of [-2,-1,0]){const pos=new T.Vector3(b.px+dx,b.py,b.pz);out['dx'+dx]=B.collides(pos,q)}
  // which parts overlap the centered spot
  const g=B.info(b.p),bx=g.geo.boundingBox.clone().applyMatrix4(new T.Matrix4().compose(new T.Vector3(b.px-1,b.py,b.pz),q,new T.Vector3(1,1,1)));out.box=[bx.min.toArray(),bx.max.toArray()];
  out.hits=[];for(const o of B.S.bricks){if(o.id===61)continue;const mm=B.meshes.get(o.id),gg=B.info(o.p);mm.updateMatrixWorld(true);const w=(gg.body||gg.geo).boundingBox.clone().applyMatrix4(mm.matrixWorld);if(w.intersectsBox(bx))out.hits.push([o.id,o.p,w.min.toArray().map(v=>+v.toFixed(2)),w.max.toArray().map(v=>+v.toFixed(2))])}
  return out}
