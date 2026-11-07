# -*- coding: utf-8 -*-
for fname in [
    'starfield-pub/tools/verify_all_expansion_modes.py',
    'starfield-pub/tools/verify_expansion_modes.py',
    'starfield-pub/tools/verify_redalert_and_dyson_modes.py'
]:
    with open(fname, 'r', encoding='utf-8') as f:
        content = f.read()
    if 'StarfieldBetaLab.setEnabled(true)' not in content:
        for target in ['await page.wait_for_timeout(1000)', 'await page.wait_for_timeout(1200)']:
            if target in content:
                content = content.replace(target, target + '\n        await page.evaluate("() => window.StarfieldBetaLab && window.StarfieldBetaLab.setEnabled(true)")\n        await page.wait_for_timeout(300)', 1)
                break
        with open(fname, 'w', encoding='utf-8') as f:
            f.write(content)
        print('Updated:', fname)
