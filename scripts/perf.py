#!/usr/bin/env python3
"""Speed check in a real browser with the full library: build, search, place parts, rotate the view.
Reports every step that blocks the screen (long tasks), with the CPU slowed down like a phone."""
import sys, json, time
from playwright.sync_api import sync_playwright
URL = sys.argv[1]
QUERIES = ['3001', 'technic beam 7', '32524', '3703', 'gear 24', 'axle 4', '6558', '3894', 'technic brick 1 x 16', 'wheel', '2780', '32062']
def note(t, m): print(f'::notice title={t}::{m}', flush=True)
with sync_playwright() as p:
    b = p.chromium.launch(args=['--use-gl=swiftshader', '--enable-unsafe-swiftshader'])
    ctx = b.new_context(viewport={'width': 412, 'height': 860}, device_scale_factor=2, is_mobile=True, has_touch=True)
    pg = ctx.new_page(); pg.set_default_timeout(15000)
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.add_init_script("window.__lt=[];new PerformanceObserver(l=>{for(const e of l.getEntries())window.__lt.push([e.startTime,e.duration])}).observe({type:'longtask',buffered:true});")
    cdp = ctx.new_cdp_session(pg); cdp.send('Emulation.setCPUThrottlingRate', {'rate': 4})
    t0 = time.time(); pg.goto(URL); pg.wait_for_timeout(6000)
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
    pg.screenshot(path='perf.png'); b.close()
