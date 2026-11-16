(function () {
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var root = document.body.getAttribute('data-root') || '';
  var norm = function (s) { return s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, ''); };

  // Pesquisa na lista de perfumes
  var q = $('#q');
  if (q) {
    var cards = [].slice.call(document.querySelectorAll('#lista .card')), n = $('#qn');
    q.addEventListener('input', function () {
      var t = norm(q.value.trim()), c = 0;
      cards.forEach(function (el) { var ok = !t || norm(el.getAttribute('data-s')).indexOf(t) > -1; el.style.display = ok ? '' : 'none'; if (ok) c++; });
      n.textContent = c + (c === 1 ? ' perfume' : ' perfumes');
    });
  }

  // Vídeo TikTok (só carrega ao clicar)
  var tb = $('#ttb');
  if (tb) tb.addEventListener('click', function () {
    var box = $('#tt'), url = box.getAttribute('data-video'), m = url.match(/\/video\/(\d+)/);
    if (!m) { window.open(url, '_blank', 'noopener'); return; }
    var d = document.createElement('div'); d.className = 'emb';
    d.innerHTML = '<blockquote class="tiktok-embed" cite="' + url.replace(/"/g, '') + '" data-video-id="' + m[1] + '" style="max-width:605px;min-width:325px;"><section></section></blockquote>';
    box.appendChild(d); tb.remove();
    var s = document.createElement('script'); s.src = 'https://www.tiktok.com/embed.js'; s.async = true; document.body.appendChild(s);
  });

  // Comentários Giscus (só carregam ao clicar)
  var gb = $('#gcb');
  if (gb) gb.addEventListener('click', function () {
    var b = $('#gc'), s = document.createElement('script');
    s.src = 'https://giscus.app/client.js'; s.async = true; s.crossOrigin = 'anonymous';
    var a = { 'data-repo': b.dataset.repo, 'data-repo-id': b.dataset.repoId, 'data-category': b.dataset.cat, 'data-category-id': b.dataset.catId,
      'data-mapping': 'specific', 'data-term': b.dataset.term, 'data-strict': '1', 'data-reactions-enabled': '1', 'data-emit-metadata': '0',
      'data-input-position': 'top', 'data-theme': 'preferred_color_scheme', 'data-lang': 'pt' };
    Object.keys(a).forEach(function (k) { s.setAttribute(k, a[k]); });
    b.innerHTML = ''; b.appendChild(s);
  });

  // Página inicial: perfume do dia + quiz
  var pdd = $('#pdd'), qz = $('#quiz');
  if (!pdd && !qz) return;
  fetch(root + 'data/perfumes.json').then(function (r) { return r.json(); }).then(function (D) {
    var F = { doce: 'Doces', fresco: 'Frescos', especiado: 'Especiados', noite: 'Noite', trabalho: 'Trabalho', date: 'Date', dia: 'Dia a dia' };
    var esc = function (s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
    var card = function (p) {
      return '<a class="card" href="' + root + 'perfumes/' + p.id + '/"><small>' + esc(p.marca) + '</small><h3>' + esc(p.nome) + '</h3><p class="np">' +
        p.notas.slice(0, 3).map(function (x) { return '<span class="pill">' + esc(x) + '</span>'; }).join('') + '</p><div>' +
        p.tags.filter(function (t) { return F[t]; }).slice(0, 3).map(function (t) { return '<span class="pill g">' + F[t] + '</span>'; }).join('') + '</div></a>';
    };
    if (pdd) {
      var d = new Date(), k = Math.floor(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()) / 864e5);
      pdd.innerHTML = card(D[k % D.length]);
    }
    if (qz) {
      var Q = [
        { t: 'Que tipo de cheiro preferes?', o: [['doce', 'Doce e envolvente'], ['fresco', 'Fresco e limpo'], ['especiado', 'Quente e especiado']], f: 'tags' },
        { t: 'Para quando é?', o: [['dia', 'Dia a dia'], ['trabalho', 'Trabalho'], ['noite', 'Noite'], ['date', 'Encontro']], f: 'ocasioes' },
        { t: 'Para que altura do ano?', o: [['verao', 'Calor'], ['inverno', 'Frio'], ['todo', 'Tanto faz']], f: 'es' }
      ], A = [], i = 0;
      var show = function () {
        if (i < Q.length) {
          qz.innerHTML = '<div class="st">PERGUNTA ' + (i + 1) + ' DE 3</div><h3>' + Q[i].t + '</h3><div class="opts">' +
            Q[i].o.map(function (o) { return '<button class="btn" type="button" data-v="' + o[0] + '">' + o[1] + '</button>'; }).join('') + '</div>';
          [].forEach.call(qz.querySelectorAll('button'), function (b) { b.onclick = function () { A[i] = b.dataset.v; i++; show(); }; });
          return;
        }
        var sc = D.map(function (p) {
          var s = 0;
          if (p.tags.indexOf(A[0]) > -1) s += 3;
          if (p.ocasioes.indexOf(A[1]) > -1 || (A[1] === 'date' && p.tags.indexOf('date') > -1)) s += 2;
          var e = p.estacao;
          if (A[2] === 'verao' && /verão/.test(e)) s += 2; else if (A[2] === 'inverno' && /inverno/.test(e)) s += 2;
          if (/todo o ano/.test(e)) s += 1;
          return [s, p];
        }).sort(function (a, b) { return b[0] - a[0] || (a[1].id < b[1].id ? -1 : 1); }).slice(0, 3);
        qz.innerHTML = '<div class="st">O TEU RESULTADO</div><h3>Experimenta estes</h3><div class="res">' +
          sc.map(function (x) { return '<a href="' + root + 'perfumes/' + x[1].id + '/"><b>' + esc(x[1].nome) + '</b> <span class="n">' + esc(x[1].marca) + '</span></a>'; }).join('') +
          '</div><button class="btn" id="qr" type="button">Refazer</button>';
        $('#qr').onclick = function () { A = []; i = 0; show(); };
      };
      show();
    }
  }).catch(function () { if (qz) qz.innerHTML = '<p class="n">Não foi possível carregar o teste.</p>'; if (pdd) pdd.innerHTML = ''; });
})();
