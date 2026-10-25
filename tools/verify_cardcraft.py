"""Headless verification for the V134 card-craft layer.

Uses --dump-dom only (never --screenshot). The probe calls
StarfieldHatch.show(), waits for the MutationObserver to build the craft DOM,
then taps twice and reads the live DOM.

Run:  python -I verify_cardcraft.py <out.html>
"""
import html
import json
import os
import re
import subprocess
import sys
import tempfile

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PREFIX = '__CARD_VERIFY__'

PROBE = """
<script>
(function(){
  var errors=[];
  window.addEventListener('error',function(e){errors.push(String(e.message||e));});
  window.addEventListener('unhandledrejection',function(e){errors.push(String(e.reason));});
  function finish(o){ o.errors=errors; document.title='__CARD_VERIFY__'+JSON.stringify(o); }
  setTimeout(function(){
    try{
      try{
        localStorage.removeItem('sf_collection_v1');
        localStorage.removeItem('sf_rolls_v1');
        localStorage.removeItem('sf_dry_v1');
      }catch(e){}
      var H=window.StarfieldHatch;
      if(!H||typeof H.show!=='function') throw new Error('StarfieldHatch.show missing');
      if(H.clear)H.clear();
      var item=H.show();
      setTimeout(function(){
        try{
          var root=document.getElementById('sf-hatch');
          var card=document.querySelector('#sf-hatch .sf-hatch-card');
          var foil=document.querySelector('#sf-hatch .sf-foil');
          var back=document.querySelector('#sf-hatch .sf-hatch-back');
          var rows=back?back.querySelectorAll('.sf-hb-row'):[];
          var fstyle=foil?getComputedStyle(foil):null;
          var data={
            item:item?{tier:item.tier,name:item.name,minutes:item.minutes,at:item.at}:null,
            overlayOn:!!(root&&root.classList.contains('on')),
            cardExists:!!card,
            foilExists:!!foil,
            foilText:foil?foil.textContent:'',
            foilOpacity:fstyle?parseFloat(fstyle.opacity):null,
            foilColor:fstyle?fstyle.color:null,
            backExists:!!back,
            rowCount:rows.length,
            rowTexts:Array.prototype.map.call(rows,function(r){return r.textContent;}),
            note:back&&back.querySelector('.sf-hb-note')?back.querySelector('.sf-hb-note').textContent:'',
            revealedAfterShow:card?card.classList.contains('revealed'):null
          };
          if(!card||!back){ finish(data); return; }
          card.click();
          data.afterFirst={
            revealed:card.classList.contains('revealed'),
            flipped:card.classList.contains('flipped')
          };
          card.click();
          data.afterSecond={
            revealed:card.classList.contains('revealed'),
            flipped:card.classList.contains('flipped')
          };
          setTimeout(function(){
            try{
              var bstyle=getComputedStyle(back);
              var f2=getComputedStyle(foil);
              data.afterSettle={
                flipped:card.classList.contains('flipped'),
                backOpacity:parseFloat(bstyle.opacity),
                foilOpacity:parseFloat(f2.opacity)
              };
              data.ok=!!(data.foilExists&&data.foilText.trim()&&data.foilOpacity>0&&
                data.backExists&&data.rowCount===3&&data.afterSecond.flipped);
              finish(data);
            }catch(e){ finish({probeError:String(e)}); }
          },500);
        }catch(e){ finish({probeError:String(e),stack:String(e&&e.stack||'')}); }
      },450);
    }catch(e){ finish({probeError:String(e),stack:String(e&&e.stack||'')}); }
  },120);
})();
</script>
"""


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: python -I verify_cardcraft.py <out.html>")
    src_p = sys.argv[1]
    with open(src_p, encoding='utf-8', newline='') as f:
        src = f.read()
    assert src.count('</body>') == 1, 'expected exactly one </body>'
    probe_src = src.replace('</body>', PROBE + '</body>', 1)

    with tempfile.TemporaryDirectory(prefix='cardverify-', ignore_cleanup_errors=True) as td:
        probe = os.path.join(td, 'probe.html')
        profile = os.path.join(td, 'profile')
        with open(probe, 'w', encoding='utf-8', newline='') as f:
            f.write(probe_src)
        url = 'file:///' + os.path.abspath(probe).replace(os.sep, '/')
        r = subprocess.run([
            CHROME, '--headless=new', '--disable-gpu',
            '--use-angle=swiftshader', '--enable-unsafe-swiftshader',
            '--disable-gpu-compositing', '--no-sandbox', '--mute-audio',
            '--no-first-run', f'--user-data-dir={profile}',
            '--window-size=1280,720', '--virtual-time-budget=7000',
            '--dump-dom', url
        ], capture_output=True, timeout=300)

    def decode(raw):
        for enc in ('utf-8-sig', 'utf-8', 'gbk', 'cp936'):
            try:
                return raw.decode(enc)
            except UnicodeDecodeError:
                pass
        return raw.decode('utf-8', errors='replace')

    out_text = decode(r.stdout)
    err_text = decode(r.stderr)
    m = re.search(r'<title>(.*?)</title>', out_text, re.S)
    if not m:
        sys.exit('NO TITLE - ' + err_text[-500:])
    title = html.unescape(m.group(1)).strip()
    if not title.startswith(PREFIX):
        sys.exit('NO PROBE TITLE - ' + title[:300])
    data = json.loads(title[len(PREFIX):])

    checks = {
        'foil_exists': data.get('foilExists') is True,
        'foil_text_nonempty': bool((data.get('foilText') or '').strip()),
        'foil_opacity_gt_0': (data.get('foilOpacity') or 0) > 0,
        'back_exists': data.get('backExists') is True,
        'three_hb_rows': data.get('rowCount') == 3,
        'flipped_after_second_click': bool((data.get('afterSecond') or {}).get('flipped')),
        'first_click_not_flipped': (data.get('afterFirst') or {}).get('flipped') is False,
        'back_visible_after_flip': ((data.get('afterSettle') or {}).get('backOpacity') or 0) > 0,
    }
    data['checks'] = checks
    data['ok'] = all(checks.values())
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    print(json.dumps(data, ensure_ascii=False, indent=2))
    if not data['ok']:
        sys.exit(1)


if __name__ == '__main__':
    main()
