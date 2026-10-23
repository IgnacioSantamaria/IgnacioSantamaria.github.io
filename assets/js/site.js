/* Publications search and project filters. No dependencies. */
(function () {
  function norm(s) { return s.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, ''); }

  /* ---- Publications: accent-insensitive search ---- */
  var input = document.getElementById('pub-search');
  if (input) {
    var status = document.getElementById('pub-status');
    var sections = [].slice.call(document.querySelectorAll('[data-pubsection]'));
    var data = sections.map(function (sec) {
      return {
        sec: sec,
        count: sec.querySelector('.count'),
        empty: sec.querySelector('.empty'),
        total: sec.querySelectorAll('.pub').length,
        items: [].slice.call(sec.querySelectorAll('.pub')).map(function (el) { return { el: el, text: norm(el.textContent) }; })
      };
    });
    var grand = data.reduce(function (n, d) { return n + d.total; }, 0);

    function apply() {
      var terms = norm(input.value).split(/\s+/).filter(Boolean), shown = 0;
      data.forEach(function (d) {
        var vis = 0, prev = null;
        d.items.forEach(function (it) {
          var ok = terms.every(function (t) { return it.text.indexOf(t) !== -1; });
          it.el.hidden = !ok;
          if (ok) {
            vis++;
            var y = it.el.getAttribute('data-year');
            it.el.classList.toggle('first-of-year', y !== prev);
            prev = y;
          }
        });
        shown += vis;
        d.count.textContent = terms.length ? vis + ' of ' + d.total : String(d.total);
        d.empty.hidden = vis !== 0;
      });
      status.textContent = terms.length ? 'Showing ' + shown + ' of ' + grand + ' publications.' : '';
    }
    input.addEventListener('input', apply);
    var q = new URLSearchParams(window.location.search).get('q');
    if (q) { input.value = q; apply(); }
  }

  /* ---- Projects: filter by funder type ---- */
  var buttons = [].slice.call(document.querySelectorAll('[data-filter]'));
  if (buttons.length) {
    var projects = [].slice.call(document.querySelectorAll('.project'));
    var groups = [].slice.call(document.querySelectorAll('[data-projsection]'));
    var pstatus = document.getElementById('proj-status');
    buttons.forEach(function (b) {
      b.addEventListener('click', function () {
        var f = b.getAttribute('data-filter'), n = 0;
        buttons.forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
        projects.forEach(function (p) {
          var ok = f === 'all' || p.getAttribute('data-type') === f;
          p.hidden = !ok; if (ok) n++;
        });
        groups.forEach(function (g) { g.hidden = !g.querySelector('.project:not([hidden])'); });
        pstatus.textContent = f === 'all' ? '' : 'Showing ' + n + ' of ' + projects.length + ' projects.';
      });
    });
  }
})();
