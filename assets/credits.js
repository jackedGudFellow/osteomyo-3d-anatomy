(function () {
  function init() {
    if (document.getElementById('credits-btn')) return;
    var btn = document.createElement('button');
    btn.type = 'button'; btn.id = 'credits-btn'; btn.className = 'theme-btn credits-btn';
    btn.title = 'Model credits (BodyParts3D, CC BY-SA) and educational-use disclaimer'; btn.setAttribute('aria-label', 'Credits and disclaimer');
    btn.textContent = '\u24D8 Credits';
    btn.setAttribute('aria-haspopup', 'dialog');
    var dlg = document.createElement('dialog');
    dlg.className = 'credits-dialog'; dlg.setAttribute('aria-labelledby', 'credits-title');
    dlg.innerHTML =
      '<h2 id="credits-title">About OsteoMyo 3D &amp; Credits</h2>' +
      '<p>3D anatomical models: <strong>BodyParts3D</strong>, © The Database Center for Life Science, ' +
      'licensed under <a href="https://creativecommons.org/licenses/by-sa/2.1/jp/" target="_blank" rel="noopener noreferrer">CC Attribution-Share Alike 2.1 Japan</a>. ' +
      'Models were processed (converted and simplified) for this app; derivative models are shared under the same license.</p>' +
      '<p>Citation: Mitsuhashi N, et al. <em>Nucleic Acids Res.</em> 2009;37:D782–5. ' +
      '<a href="https://lifesciencedb.jp/bp3d/" target="_blank" rel="noopener noreferrer">lifesciencedb.jp/bp3d</a></p>' +
      '<p>3D rendering: <a href="https://threejs.org/" target="_blank" rel="noopener noreferrer">three.js</a> (MIT).</p>' +
      '<p class="credits-warn"><strong>Educational use only.</strong> This atlas is a study aid. It is not a medical device ' +
      'and must not be used for diagnosis, treatment or clinical decisions. Always verify against standard anatomical references.</p>' +
      '<form method="dialog"><button type="submit" autofocus>Close</button></form>';
    btn.addEventListener('click', function () {
      if (typeof dlg.showModal === 'function') dlg.showModal(); else dlg.setAttribute('open', '');
    });
    dlg.addEventListener('click', function (e) { if (e.target === dlg) dlg.close(); });
    var host = document.querySelector('.top-actions');
    if (host) host.appendChild(btn); else { btn.classList.add('credits-btn-floating'); document.body.appendChild(btn); }
    document.body.appendChild(dlg);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
