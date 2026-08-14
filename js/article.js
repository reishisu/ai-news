// AIで作る技術 — 記事ページの手触りを良くする小物
// 読了プログレス / コードのコピー / クイズ / チェックリスト / 数字のカウントアップ
(function () {
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- 読了プログレスバー ---------- */
  var bar = document.createElement("div");
  bar.className = "read-progress";
  bar.innerHTML = '<i></i>';
  document.body.appendChild(bar);
  var fill = bar.firstChild;
  function updateProgress() {
    var h = document.documentElement;
    var max = h.scrollHeight - h.clientHeight;
    var p = max > 0 ? (h.scrollTop / max) * 100 : 0;
    fill.style.width = p.toFixed(1) + "%";
  }
  document.addEventListener("scroll", updateProgress, { passive: true });
  updateProgress();

  /* ---------- コードのコピーボタン ---------- */
  document.querySelectorAll(".code").forEach(function (box) {
    var head = box.querySelector(".code-head");
    var pre = box.querySelector("pre");
    if (!head || !pre) return;
    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "copy-btn";
    btn.textContent = "コピー";
    head.appendChild(btn);
    btn.addEventListener("click", function () {
      var text = pre.innerText.replace(/^\$ /gm, "");
      (navigator.clipboard ? navigator.clipboard.writeText(text) : Promise.reject())
        .then(function () {
          btn.textContent = "コピーした ✓";
          btn.classList.add("done");
          setTimeout(function () { btn.textContent = "コピー"; btn.classList.remove("done"); }, 1600);
        })
        .catch(function () { window.prompt("コピーしてください", text); });
    });
  });

  /* ---------- クイズ ---------- */
  document.querySelectorAll(".quiz").forEach(function (quiz) {
    var answer = quiz.querySelector(".ans");
    quiz.querySelectorAll(".opt").forEach(function (opt) {
      opt.addEventListener("click", function () {
        if (quiz.classList.contains("answered")) return;
        quiz.classList.add("answered");
        var correct = opt.dataset.correct === "true";
        opt.classList.add(correct ? "right" : "wrong");
        quiz.querySelectorAll(".opt").forEach(function (o) {
          if (o.dataset.correct === "true") o.classList.add("right");
          o.disabled = true;
        });
        if (answer) answer.hidden = false;
        if (correct && !reduce) burst(opt);
      });
    });
  });

  /* ---------- チェックリスト(進捗は端末に保存) ---------- */
  document.querySelectorAll(".checklist").forEach(function (list) {
    var key = "ai-news-check-" + (list.dataset.key || "default");
    var boxes = list.querySelectorAll('input[type="checkbox"]');
    var done = list.parentElement.querySelector(".cl-done");
    var saved = {};
    try { saved = JSON.parse(localStorage.getItem(key) || "{}"); } catch (e) {}

    function refresh(fromClick) {
      var n = 0;
      boxes.forEach(function (b) { if (b.checked) n++; });
      var all = n === boxes.length && boxes.length > 0;
      if (done) {
        done.hidden = !all;
        if (all && fromClick && !reduce) burst(done);
      }
      var counter = list.parentElement.querySelector(".cl-count");
      if (counter) counter.textContent = n + " / " + boxes.length;
    }

    boxes.forEach(function (b, i) {
      b.checked = !!saved[i];
      b.addEventListener("change", function () {
        saved[i] = b.checked;
        try { localStorage.setItem(key, JSON.stringify(saved)); } catch (e) {}
        b.closest("li").classList.toggle("checked", b.checked);
        refresh(true);
      });
      b.closest("li").classList.toggle("checked", b.checked);
    });
    refresh(false);
  });

  /* ---------- 数字のカウントアップ ---------- */
  var counters = document.querySelectorAll("[data-count]");
  if (counters.length) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        io.unobserve(e.target);
        var el = e.target;
        var target = parseFloat(el.dataset.count);
        if (reduce) { el.textContent = el.dataset.count; return; }
        var start = performance.now(), dur = 900;
        (function tick(now) {
          var t = Math.min((now - start) / dur, 1);
          var eased = 1 - Math.pow(1 - t, 3);
          var v = target * eased;
          el.textContent = Number.isInteger(target) ? Math.round(v) : v.toFixed(1);
          if (t < 1) requestAnimationFrame(tick);
        })(start);
      });
    }, { threshold: 0.6 });
    counters.forEach(function (c) { io.observe(c); });
  }

  /* ---------- セクションのふわっと表示 ---------- */
  if (!reduce) {
    var items = document.querySelectorAll(".item, figure, .quiz");
    items.forEach(function (el) { el.classList.add("reveal"); });
    var io2 = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add("shown"); io2.unobserve(e.target); }
      });
    }, { threshold: 0.08, rootMargin: "0px 0px -40px 0px" });
    items.forEach(function (el) { io2.observe(el); });
  }

  /* ---------- ちいさな祝福 ---------- */
  function burst(anchor) {
    var rect = anchor.getBoundingClientRect();
    var colors = ["#2a78d6", "#26c08a", "#eda100", "#eb6834", "#a78bfa"];
    for (var i = 0; i < 14; i++) {
      var dot = document.createElement("i");
      dot.className = "confetti";
      dot.style.left = rect.left + rect.width / 2 + "px";
      dot.style.top = rect.top + rect.height / 2 + "px";
      dot.style.background = colors[i % colors.length];
      var angle = (Math.PI * 2 * i) / 14;
      var dist = 60 + (i % 4) * 18;
      dot.style.setProperty("--dx", Math.cos(angle) * dist + "px");
      dot.style.setProperty("--dy", Math.sin(angle) * dist + "px");
      document.body.appendChild(dot);
      setTimeout(function (d) { return function () { d.remove(); }; }(dot), 900);
    }
  }
})();
