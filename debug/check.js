async()=>{const B=window.__bs,out={};
 try{const bx=x=>x?[x.min,x.max].map(v=>v.toArray().map(n=>+n.toFixed(3))):null;
  for(const p of ['ld:32013','ld:3706','ld:32526']){const g=B.info(p);out[p]={conns:g.conns,h:g.h,geo:bx(g.geo.boundingBox),body:g.body?bx(g.body.boundingBox):null,nsnaps:(g.snaps||[]).length}}
  for(const id of [130,129,128]){const b=B.brickById(id),m=B.meshes.get(id);out['b'+id]={p:b.p,pos:m.position.toArray(),q:m.quaternion.toArray()}}
 }catch(e){out.err=String(e)}
 return out}
