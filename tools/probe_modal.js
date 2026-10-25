<script>
document.getElementById('begin').click();
var S = window.Starfield; if (S && S.seek) S.seek(40);
document.getElementById('settings-toggle').click();
setTimeout(function () {
  var c = getComputedStyle(document.getElementById('comms-hud'));
  document.title = JSON.stringify({
    body: document.body.className,
    drawer: document.getElementById('settings-drawer').className,
    modal: (window.Starfield && typeof window.Starfield.isModalOpen==='function') ? window.Starfield.isModalOpen() : 'no-method',
    commsOpacity: c.opacity, hidden: document.hidden, vis: document.visibilityState, frames: window.__t||0, mo: window.__mo, err: window.__err||null, draws: (S&&S.getState)?S.getState().drawCalls:null, tabs: Array.prototype.map.call(document.querySelectorAll('.codex-tab'),function(t){return t.offsetWidth}), tabBox: document.querySelector('.codex-tabs')?document.querySelector('.codex-tabs').clientWidth:null
  });
}, 700);
</script>
