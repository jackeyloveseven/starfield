import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        page = browser.new_page(viewport={'width': 1024, 'height': 768})
        
        console_errors = []
        page.on('pageerror', lambda err: console_errors.append(str(err)))
        
        file_url = 'file:///' + os.path.abspath('starfield-pub/starfield.html').replace('\\', '/')
        print('Testing URL:', file_url)
        page.goto(file_url, wait_until='networkidle')
        page.wait_for_timeout(800)
        
        # Start game
        page.locator('#begin').click()
        page.wait_for_timeout(1000)
        
        # Verify Soundscape and Jukebox
        res = page.evaluate('''() => {
            const sound = window.sound || (window.Starfield ? window.Starfield.getSoundscape() : null);
            const btns = Array.from(document.querySelectorAll('.track-select-btn'));
            const titleEl = document.getElementById('classical-track-title');
            const descEl = document.getElementById('classical-track-composer');
            
            return {
                hasSound: !!sound,
                mediaCount: sound && sound.media ? sound.media.length : 0,
                originalTracksCount: sound && sound.originalTracks ? sound.originalTracks.length : 0,
                btnCount: btns.length,
                btn7Text: btns[6] ? btns[6].textContent.trim() : null,
                initialTitle: titleEl ? titleEl.textContent.trim() : null
            };
        }''')
        print('Initial check:', res)
        assert res['mediaCount'] == 7, f"Expected 7 media tracks, got {res['mediaCount']}"
        assert res['btnCount'] == 7, f"Expected 7 track buttons, got {res['btnCount']}"
        assert 'Better Call Saul' in res['btn7Text'], 'Button 7 should mention Better Call Saul'
        
        # Click track 7 (0-indexed 6)
        page.evaluate('''() => {
            const btns = document.querySelectorAll('.track-select-btn');
            if (btns[6]) btns[6].click();
        }''')
        page.wait_for_timeout(600)
        
        switched_res = page.evaluate('''() => {
            const sound = window.sound || (window.Starfield ? window.Starfield.getSoundscape() : null);
            const titleEl = document.getElementById('classical-track-title');
            const descEl = document.getElementById('classical-track-composer');
            const activeBtn = document.querySelector('.track-select-btn.active');
            
            return {
                currentIndex: sound ? sound.index : -1,
                activeDataTrack: activeBtn ? activeBtn.getAttribute('data-track') : null,
                titleText: titleEl ? titleEl.textContent.trim() : null,
                descText: descEl ? descEl.textContent.trim() : null,
                isPlaying: sound && sound.media && sound.media[6] ? !sound.media[6].paused : false
            };
        }''')
        print('Switched to Track 7:', switched_res)
        assert switched_res['currentIndex'] == 6, 'Should switch to index 6'
        assert switched_res['activeDataTrack'] == '6', 'Active button data-track should be 6'
        assert 'Better Call Saul' in switched_res['titleText'], 'Track title should update to Better Call Saul'
        assert 'Little Barrie' in switched_res['descText'], 'Track desc should update to Little Barrie'
        
        # Test next track wrap-around
        page.locator('#btn-next-track').click()
        page.wait_for_timeout(400)
        wrapped_res = page.evaluate('''() => {
            const sound = window.sound || (window.Starfield ? window.Starfield.getSoundscape() : null);
            return {
                currentIndex: sound ? sound.index : -1
            };
        }''')
        print('After next track wrap-around:', wrapped_res)
        assert wrapped_res['currentIndex'] == 0, 'Index should wrap back to 0'
        
        # Test prev track wrap-around
        page.locator('#btn-prev-track').click()
        page.wait_for_timeout(400)
        prev_wrapped_res = page.evaluate('''() => {
            const sound = window.sound || (window.Starfield ? window.Starfield.getSoundscape() : null);
            return {
                currentIndex: sound ? sound.index : -1
            };
        }''')
        print('After prev track wrap-around back to 6:', prev_wrapped_res)
        assert prev_wrapped_res['currentIndex'] == 6, 'Index should wrap back to 6'
        
        # Open drawer and take screenshot
        page.evaluate('''() => {
            const drawer = document.getElementById('settings-drawer');
            if (drawer) drawer.classList.add('open');
        }''')
        page.wait_for_timeout(500)
        shot_path = 'starfield-pub/tools/test_jukebox_track7.png'
        page.screenshot(path=shot_path)
        print('Saved screenshot to:', shot_path)
        
        browser.close()

    print('Console errors count:', len(console_errors))
    if console_errors:
        print('Errors:', console_errors)
    assert len(console_errors) == 0, f'Errors: {console_errors}'
    print('ALL JUKEBOX TRACK 7 VERIFICATIONS PASSED!')

if __name__ == '__main__':
    main()
