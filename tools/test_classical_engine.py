"""
Test Classical Music Engine in Headless Chromium with Playwright
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

test_html = """<!doctype html>
<html>
<head><meta charset="utf-8"><title>Test Classical Engine</title></head>
<body>
<h1>Classical Engine Test</h1>
<button id="btn-start">Start Audio</button>
<script src="classical_music_engine.js"></script>
<script>
window.testResults = {};
document.getElementById('btn-start').addEventListener('click', async () => {
    try {
        const AC = window.AudioContext || window.webkitAudioContext;
        const ac = new AC();
        await ac.resume();
        const master = ac.createGain();
        master.connect(ac.destination);
        
        const engine = new ClassicalMusicEngine(ac, master);
        window.engine = engine;
        
        const pieces = engine.getAllPieces();
        window.testResults.piecesCount = pieces.length;
        window.testResults.pieces = pieces.map(p => p.title);
        
        // Play track 0 (Clair de lune)
        engine.playTrack(0, false);
        window.testResults.track0Playing = engine.isPlaying;
        window.testResults.current0 = engine.getCurrentPiece().id;
        
        // Advance to track 1 (Gymnopedie 1)
        engine.nextTrack(false);
        window.testResults.current1 = engine.getCurrentPiece().id;
        
        // Advance to track 3 (Air on the G string)
        engine.playTrack(3, false);
        window.testResults.current3 = engine.getCurrentPiece().id;
        
        window.testResults.success = true;
    } catch (e) {
        window.testResults.error = e.toString();
    }
});
</script>
</body>
</html>
"""

with open('d:/items/code/starfield-pub/tools/test_classical.html', 'w', encoding='utf-8') as f:
    f.write(test_html)

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page()
    page.goto('file:///d:/items/code/starfield-pub/tools/test_classical.html')
    page.click('#btn-start')
    page.wait_for_timeout(1000)
    res = page.evaluate('() => window.testResults')
    print("Test results:", res)
    assert res.get('success'), f"Test failed: {res}"
    print("ALL CLASSICAL MUSIC ENGINE TESTS PASSED!")
    browser.close()
