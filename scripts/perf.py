#!/usr/bin/env python3
"""Speed check in a real browser with the full library: build, search, place parts, rotate the view.
Reports every step that blocks the screen (long tasks), with the CPU slowed down like a phone."""
import sys, json, time
from playwright.sync_api import sync_playwright
URL = sys.argv[1]
QUERIES = ['3001', 'technic beam 7', '32524', '3703', 'gear 24', 'axle 4', '6558', '3894', 'technic brick 1 x 16', 'wheel', '2780', '32062']
LINES = []
def note(t, m): LINES.append(f'{t}: {m}')
def flush():
    for i in range(0, len(LINES), 8):
        print('::notice title=perf %d::' % (i // 8) + '%0A'.join(LINES[i:i + 8]).replace('::', ' '), flush=True)
with sync_playwright() as p:
    b = p.chromium.launch(args=['--use-gl=swiftshader', '--enable-unsafe-swiftshader'])
    ctx = b.new_context(viewport={'width': 412, 'height': 860}, device_scale_factor=2, is_mobile=True, has_touch=True)
    pg = ctx.new_page(); pg.set_default_timeout(15000)
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.add_init_script("window.__lt=[];new PerformanceObserver(l=>{for(const e of l.getEntries())window.__lt.push([e.startTime,e.duration])}).observe({type:'longtask',buffered:true});")
    cdp = ctx.new_cdp_session(pg); cdp.send('Emulation.setCPUThrottlingRate', {'rate': 4})
    cdp.send('Profiler.enable'); cdp.send('Profiler.setSamplingInterval', {'interval': 500})
    t0 = time.time(); pg.goto(URL); pg.wait_for_timeout(6000); cdp.send('Profiler.start')
    def window(label, fn):
        a = pg.evaluate('performance.now()'); fn(); z = pg.evaluate('performance.now()')
        lt = pg.evaluate(f'window.__lt.filter(e=>e[0]>={a}&&e[0]<={z})')
        tot = sum(d for _, d in lt); mx = max([d for _, d in lt] or [0])
        note('step ' + label, f'{(z-a)/1000:.1f}s, blocked {tot/1000:.1f}s, longest freeze {mx/1000:.2f}s ({len(lt)} freezes)')
        return mx
    window('open page', lambda: None)
    try:
        if pg.is_visible('.proj .open'): window('open project', lambda: (pg.click('.proj .open'), pg.wait_for_timeout(3000)))
        else: window('new project', lambda: (pg.click('#newProj'), pg.wait_for_timeout(500), pg.click('#npGo'), pg.wait_for_timeout(3000)))
    except Exception as e: note('open', str(e)[:200])
    box = pg.query_selector('#stage canvas').bounding_box(); cx, cy = box['x'] + box['width'] / 2, box['y'] + box['height'] * .6
    for i, q in enumerate(QUERIES):
        def step():
            pg.fill('#q', q); pg.wait_for_timeout(3000)
            parts = pg.query_selector_all('#parts .part')
            if not parts: return
            parts[0].click(); pg.wait_for_timeout(1500)
            pg.mouse.click(cx + (i % 4 - 1.5) * 40, cy + (i // 4 - 1) * 40); pg.wait_for_timeout(800)
            if pg.is_visible('#okBtn') and pg.is_enabled('#okBtn'): pg.click('#okBtn')
            pg.wait_for_timeout(2000)
        try: window(f'search+place "{q}"', step)
        except Exception as e: note('fail ' + q, str(e)[:200])
    def drag():
        pg.mouse.move(cx, cy); pg.mouse.down(); pg.mouse.move(cx + 150, cy + 30, steps=30); pg.mouse.up(); pg.wait_for_timeout(1000)
    window('rotate view', drag)
    def select():
        pg.click('[data-mode="select"]'); pg.wait_for_timeout(300); pg.mouse.click(cx, cy); pg.wait_for_timeout(800)
        for _ in range(4):
            if pg.is_visible('[data-mv="r"]'): pg.click('[data-mv="r"]'); pg.wait_for_timeout(300)
        if pg.is_visible('#okBtn') and pg.is_enabled('#okBtn'): pg.click('#okBtn')
        pg.wait_for_timeout(1500)
    try: window('select and move', select)
    except Exception as e: note('fail select', str(e)[:200])
    window('idle 5s', lambda: pg.wait_for_timeout(5000))
    n = pg.evaluate("document.querySelector('#count').textContent")
    heap = pg.evaluate("performance.memory?Math.round(performance.memory.usedJSHeapSize/1e6):-1")
    note('summary', f'{n}, heap {heap}MB, errors: {errs[:3]}')
    prof = cdp.send('Profiler.stop')['profile']
    nodes = {n['id']: n for n in prof['nodes']}; dt = prof.get('timeDeltas', []); self_t = {}
    for sid, d in zip(prof.get('samples', []), dt):
        n = nodes[sid]['callFrame']; k = (n['functionName'] or '(anon)') + ':' + str(n.get('lineNumber', 0) + 1) + (' ' + n['url'].split('/')[-1] if n.get('url') else '')
        self_t[k] = self_t.get(k, 0) + d
    tot = sum(self_t.values()) or 1
    # also inclusive time per function of our page
    parent = {}
    for n in prof['nodes']:
        for c in n.get('children', []): parent[c] = n['id']
    incl = {}
    for sid, d in zip(prof.get('samples', []), dt):
        seen = set(); x = sid
        while x is not None:
            cf = nodes[x]['callFrame']
            if 'index.html' in cf.get('url', ''):
                k = (cf['functionName'] or '(anon)') + ':' + str(cf.get('lineNumber', 0) + 1)
                if k not in seen: incl[k] = incl.get(k, 0) + d; seen.add(k)
            x = parent.get(x)
    for k, v in sorted(self_t.items(), key=lambda kv: -kv[1])[:16]: note('self', f'{v/1e6:.1f}s {100*v/tot:.0f}% {k}')
    for k, v in sorted(incl.items(), key=lambda kv: -kv[1])[:24]: note('incl', f'{v/1e6:.1f}s {k}')
    flush(); pg.screenshot(path='perf.png'); b.close()
