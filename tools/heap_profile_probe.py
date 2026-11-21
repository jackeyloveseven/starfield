# tools/heap_profile_probe.py
from playwright.sync_api import sync_playwright
import os, json

HTML_FILE = os.path.abspath(r'd:\items\code\projects\starfield\starfield-pub\starfield.html')
file_url = 'file:///' + HTML_FILE.replace('\\', '/')

with sync_playwright() as p:
    browser = p.chromium.launch(
        channel='chrome',
        headless=True,
        args=['--enable-webgl', '--no-sandbox', '--js-flags=--expose-gc', '--enable-precise-memory-info']
    )
    context = browser.new_context(viewport={'width': 412, 'height': 915}, device_scale_factor=3.0)
    page = context.new_page()
    cdp = context.new_cdp_session(page)
    cdp.send('HeapProfiler.enable')
    
    page.goto(file_url)
    page.wait_for_timeout(1000)
    page.click('#begin')
    page.wait_for_timeout(1000)
    
    # Start sampling heap profiler
    cdp.send('HeapProfiler.startSampling', {'samplingInterval': 16384})
    page.wait_for_timeout(3000)
    profile = cdp.send('HeapProfiler.stopSampling')
    
    samples = []
    def walk(node, depth=0):
        call = node.get('callFrame', {})
        self_size = node.get('selfSize', 0)
        fn_name = call.get('functionName', '(anon)')
        line = call.get('lineNumber', 0)
        col = call.get('columnNumber', 0)
        if self_size > 50000:
            samples.append({'fn': fn_name, 'line': line, 'col': col, 'size': self_size, 'depth': depth})
        for child in node.get('children', []):
            walk(child, depth + 1)
            
    walk(profile['profile']['head'])
    samples.sort(key=lambda x: x['size'], reverse=True)
    print('Top Allocation Call Sites:')
    for s in samples[:20]:
        print(f"  {s['fn']} @ L{s['line']}:{s['col']} -> {s['size']/1024:.1f} KB")
        
    browser.close()
