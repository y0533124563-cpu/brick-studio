async()=>{const B=window.__bs,out={};
 try{B.pickUp(130);await new Promise(r=>setTimeout(r,1500));const s=B.sel,M=B.MOVE;
  out.sel=s?{kind:s.kind,bad:s.bad,bid:s.bid}:null;out.move=M?{id:M.b&&M.b.id,copy:M.copy}:null;out.part=B.S.part;out.isPin=B.isPinPart(B.S.part);out.needs=B.needsCheck(s);
  const T=THREE;out.keys=Object.keys(s);const pos=s.pos.clone(),q=(s.q||new T.Quaternion()).clone();
  out.pos=pos.toArray();out.collides=B.collides(pos,q);
  const {mn,mx}=B.qBox(B.S.part,q);const hb=new T.Box3(mn.clone().add(pos),mx.clone().add(pos));out.hb=[hb.min.toArray(),hb.max.toArray()];
  out.mated=[...B.matedIds(pos,q)];
  out.hits=[];for(const bb of B.S.bricks){if(bb.id===130)continue;const mm=B.meshes.get(bb.id);if(!mm)continue;mm.updateMatrixWorld(true);const g=B.info(bb.p),w=(g.body||g.geo).boundingBox.clone().applyMatrix4(mm.matrixWorld);if(hb.intersectsBox(w)){const i=hb.clone().intersect(w);out.hits.push([bb.id,bb.p,B.isPinPart(bb.p),+(Math.max(0,i.max.x-i.min.x)*Math.max(0,i.max.y-i.min.y)*Math.max(0,i.max.z-i.min.z)).toFixed(3),w.min.toArray().map(v=>+v.toFixed(2)),w.max.toArray().map(v=>+v.toFixed(2))])}}
 }catch(e){out.err=String(e)}
 return out}
