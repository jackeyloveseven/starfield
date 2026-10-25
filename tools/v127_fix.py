"""V127: three things the phone reported.

1. "变模糊了，像素感很强" - my own adaptive scaler dropped DPR to 0.55x as soon as
   the frame rate dipped below 75% of the panel. At 50 fps that is a blurry
   picture. The floor is now 0.8x and it only drops below 60% of target.
2. a long press opened the browser's lens/context menu over the canvas.
3. system Back exited the app even with a sheet open.
"""
import sys
src_p,out_p=sys.argv[1],sys.argv[2]
src=open(src_p,encoding="utf-8").read()
def rep(a,b):
    global src
    n=src.count(a)
    if n!=1: sys.exit("count=%d: %r"%(n,a[:90]))
    src=src.replace(a,b,1)

rep("if(fps<target*0.75&&qualityScale>.55){qualityScale=Math.max(.55,qualityScale-.15);resize();}",
    "if(fps<target*0.6&&qualityScale>.8){qualityScale=Math.max(.8,qualityScale-.1);resize();}")

rep("</head>",
"""<style id="sf-touch-guard">
/* A long press on the artwork popped the browser's image search / context menu. */
html,body,#world,#landscape{-webkit-touch-callout:none;-webkit-user-select:none;user-select:none}
img,canvas{-webkit-user-drag:none;user-drag:none}
</style>
</head>""")

rep("</body>",
"""<script>
(function(){
  document.addEventListener('contextmenu',function(e){ e.preventDefault(); },{passive:false});
  // One place for system Back: close whatever is on top, else let the app exit.
  window.__sfBack=function(){
    var h=document.getElementById('sf-hatch'); if(h&&h.classList.contains('on')){h.classList.remove('on');return true;}
    var l=document.getElementById('sf-hatch-list'); if(l&&l.classList.contains('on')){l.classList.remove('on');return true;}
    var c=document.getElementById('codex-modal'); if(c&&c.classList.contains('open')){var b=c.querySelector('.codex-close');if(b){b.click();return true;}}
    var d=document.getElementById('settings-drawer'); if(d&&d.classList.contains('open')){var s=document.getElementById('settings-close-btn');if(s){s.click();return true;}}
    return false;
  };
})();
</script>
</body>""")
open(out_p,"w",encoding="utf-8",newline="").write(src)
print("V127 written:",len(src),"chars")
