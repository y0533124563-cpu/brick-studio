#!/usr/bin/env python3
"""Open a model code in the real app (full library) and save pictures + numbers about how parts sit, for debugging."""
import sys, json
from playwright.sync_api import sync_playwright
URL, CODE, OUT = sys.argv[1], open(sys.argv[2]).read().strip(), sys.argv[3]
FOCUS = [int(x) for x in sys.argv[4].split(',') if x.strip()] if len(sys.argv) > 4 else []
with sync_playwright() as p:
    b = p.chromium.launch(args=['--use-gl=swiftshader', '--enable-unsafe-swiftshader'])
    pg = b.new_page(viewport={'width': 1400, 'height': 900}); pg.set_default_timeout(120000)
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.add_init_script("sessionStorage.setItem('bs:app','1')")
    pg.goto(URL); pg.wait_for_timeout(4000)
    pg.evaluate("c=>{const B=window.__bs;B.openProject({id:'dbg',name:'dbg',data:JSON.stringify(B.decode(c)),plate:{w:48,d:48}})}", CODE)
    try: pg.wait_for_function("()=>window.__bs.S.bricks.every(b=>window.__bs.meshes.get(b.id))", timeout=180000)
    except Exception as e: errs.append('wait: '+str(e)[:300]); pg.wait_for_timeout(3000)
    info = pg.evaluate("""f=>{const B=window.__bs,out=[];const bb=id=>{const m=B.meshes.get(id),g=B.info(B.brickById(id).p);m.updateMatrixWorld(true);return (g.body||g.geo).boundingBox.clone().applyMatrix4(m.matrixWorld)};
      for(const b of B.S.bricks){const x=bb(b.id);out.push({i:b.id,p:b.p,c:b.c,min:x.min.toArray().map(v=>+v.toFixed(3)),max:x.max.toArray().map(v=>+v.toFixed(3)),h:B.info(b.p).h,snaps:(B.info(b.p).snaps||[]).length})}
      return out}""", FOCUS)
    import os
    try: extra = pg.evaluate(open('debug/check.js').read()) if os.path.exists('debug/check.js') else None
    except Exception as e: extra = {'check_error': str(e)[:2000]}
    json.dump({'parts': info, 'errors': errs, 'check': extra}, open(OUT + '/parts.json', 'w'), indent=1)
    shots = [('all', None)] + [(f'part{i}', i) for i in FOCUS]
    for name, i in shots:
        for k, (a, el, d) in enumerate([(0.6, 0.55, 1.0), (2.2, 0.25, 0.7), (-1.0, 0.12, 0.55), (3.6, 0.1, 0.5)]):
            pg.evaluate("""([i,a,el,d])=>{const B=window.__bs,T=THREE;let c,r;if(i){const m=B.meshes.get(i),g=B.info(B.brickById(i).p);m.updateMatrixWorld(true);const x=(g.body||g.geo).boundingBox.clone().applyMatrix4(m.matrixWorld);c=x.getCenter(new T.Vector3());r=Math.max(6,x.getSize(new T.Vector3()).length()*2.2)}
              else{const x=new T.Box3();for(const m of B.meshes.values())x.expandByObject(m);c=x.getCenter(new T.Vector3());r=x.getSize(new T.Vector3()).length()*1.1}
              const p=c.clone().add(new T.Vector3(Math.sin(a)*Math.cos(el),Math.sin(el),Math.cos(a)*Math.cos(el)).multiplyScalar(r*d));B.camTo(p,c)}""", [i, a, el, d])
            pg.wait_for_timeout(1500); pg.screenshot(path=f'{OUT}/{name}_{k}.png')
    b.close()
print('done', errs)
