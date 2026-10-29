import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

def main():
    html_rel = 'starfield.html' if os.path.exists('starfield.html') else 'starfield-pub/starfield.html'
    file_url = 'file:///' + os.path.abspath(html_rel).replace('\\', '/')
    print('Testing URL:', file_url)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        page = browser.new_page(viewport={'width': 1024, 'height': 768})
        
        console_errors = []
        page.on('pageerror', lambda err: console_errors.append(str(err)))
        
        page.goto(file_url, wait_until='networkidle')
        page.wait_for_timeout(800)
        
        # Start game
        page.locator('#begin').click()
        page.wait_for_timeout(1000)
        
        # 1. Verify Soundscape has 8 tracks
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
                btn8Text: btns[7] ? btns[7].textContent.trim() : null,
                initialTitle: titleEl ? titleEl.textContent.trim() : null
            };
        }''')
        print('Initial check:', res)
        assert res['mediaCount'] == 8, f"Expected 8 media tracks, got {res['mediaCount']}"
        assert res['btnCount'] == 8, f"Expected 8 track buttons, got {res['btnCount']}"
        assert 'Better Call Saul' in res['btn7Text'], 'Button 7 should mention Better Call Saul'
        assert '四月是你的谎言' in res['btn8Text'], 'Button 8 should mention 四月是你的谎言'
        assert '圣-桑' in res['btn8Text'] or '圣桑' in res['btn8Text'], 'Button 8 should mention 圣-桑'
        
        # 2. Switch to Track 8 (0-indexed 7)
        print('\n--- Testing Track 8: 四月是你的谎言 圣·桑 引子与回旋随想曲 Op.28 ---')
        page.evaluate('''() => {
            const btns = document.querySelectorAll('.track-select-btn');
            if (btns[7]) btns[7].click();
        }''')
        page.wait_for_timeout(800)
        
        switched_res = page.evaluate('''() => {
            const sound = window.sound || (window.Starfield ? window.Starfield.getSoundscape() : null);
            const titleEl = document.getElementById('classical-track-title');
            const descEl = document.getElementById('classical-track-composer');
            const activeBtn = document.querySelector('.track-select-btn.active');
            const media8 = sound && sound.media ? sound.media[7] : null;
            
            return {
                currentIndex: sound ? sound.index : -1,
                activeDataTrack: activeBtn ? activeBtn.getAttribute('data-track') : null,
                titleText: titleEl ? titleEl.textContent.trim() : null,
                descText: descEl ? descEl.textContent.trim() : null,
                isPlaying: media8 ? !media8.paused : false,
                duration: media8 ? media8.duration : 0
            };
        }''')
        print('Switched to Track 8:', switched_res)
        assert switched_res['currentIndex'] == 7, 'Should switch to index 7'
        assert switched_res['activeDataTrack'] == '7', 'Active button data-track should be 7'
        assert '四月是你的谎言' in switched_res['titleText'], 'Title should mention 四月是你的谎言'
        assert '引子与回旋随想曲' in switched_res['titleText'], 'Title should mention 引子与回旋随想曲'
        assert '篠原悠那' in switched_res['descText'], 'Desc should credit 篠原悠那'
        assert switched_res['duration'] > 550, f"Expected full master duration ~561s, got {switched_res['duration']}"
        assert switched_res['isPlaying'], 'Track 8 should be playing'
        
        # 3. Test wrap-around from Track 8 to Track 1
        print('\n--- Testing Wrap-around next track: 7 -> 0 ---')
        page.locator('#btn-next-track').click()
        page.wait_for_timeout(400)
        wrapped_res = page.evaluate('''() => {
            const sound = window.sound || (window.Starfield ? window.Starfield.getSoundscape() : null);
            return { currentIndex: sound ? sound.index : -1 };
        }''')
        print('After next track wrap-around:', wrapped_res)
        assert wrapped_res['currentIndex'] == 0, 'Index should wrap back to 0'
        
        # 4. Test wrap-around backwards from Track 1 to Track 8
        print('\n--- Testing Wrap-around prev track: 0 -> 7 ---')
        page.locator('#btn-prev-track').click()
        page.wait_for_timeout(400)
        prev_wrapped_res = page.evaluate('''() => {
            const sound = window.sound || (window.Starfield ? window.Starfield.getSoundscape() : null);
            return { currentIndex: sound ? sound.index : -1 };
        }''')
        print('After prev track wrap-around back to 7:', prev_wrapped_res)
        assert prev_wrapped_res['currentIndex'] == 7, 'Index should wrap back to 7'
        
        # 5. Test keyboard shortcut 'N' (Next track)
        print('\n--- Testing Keyboard shortcut N ---')
        page.keyboard.press('n')
        page.wait_for_timeout(400)
        k_res = page.evaluate('''() => {
            const sound = window.sound || (window.Starfield ? window.Starfield.getSoundscape() : null);
            return { currentIndex: sound ? sound.index : -1 };
        }''')
        print('After pressing N:', k_res)
        assert k_res['currentIndex'] == 0, 'Pressing N should advance to index 0'
        
        # 6. Test keyboard shortcut 'B' (Prev track)
        print('\n--- Testing Keyboard shortcut B ---')
        page.keyboard.press('b')
        page.wait_for_timeout(400)
        kb_res = page.evaluate('''() => {
            const sound = window.sound || (window.Starfield ? window.Starfield.getSoundscape() : null);
            return { currentIndex: sound ? sound.index : -1 };
        }''')
        print('After pressing B:', kb_res)
        assert kb_res['currentIndex'] == 7, 'Pressing B should go back to index 7'
        
        # Open drawer and take screenshot of Jukebox
        page.evaluate('''() => {
            const drawer = document.getElementById('settings-drawer');
            if (drawer) drawer.classList.add('open');
        }''')
        page.wait_for_timeout(500)
        shot_path = os.path.join(os.path.dirname(__file__), '..', 'shots', 'test_jukebox_track8.png')
        page.screenshot(path=shot_path)
        print('Saved screenshot to:', shot_path)
        
        browser.close()

    print('Console errors count:', len(console_errors))
    assert len(console_errors) == 0, f'Errors: {console_errors}'
    print('\n🎉 ALL JUKEBOX TRACK 8 (SHIGATSU RONDO 9:15) VERIFICATIONS PASSED 100%!')

if __name__ == '__main__':
    main()
