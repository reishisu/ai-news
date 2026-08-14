// ホームの検索とタグ絞り込み。URLに ?q= と ?tag= を保存するので、共有・再訪でも状態が残る。
(function () {
  var input = document.getElementById("searchInput");
  var clearBtn = document.getElementById("searchClear");
  var tagBar = document.getElementById("tagBar");
  var list = document.getElementById("postList");
  var hitCount = document.getElementById("hitCount");
  var noHit = document.getElementById("noHit");
  if (!input || !list) return;

  var cards = [].slice.call(list.querySelectorAll(".post-card"));
  var state = { q: "", tag: "" };

  function normalize(s) {
    return (s || "").toLowerCase().replace(/\s+/g, " ").trim();
  }

  function apply(pushUrl) {
    var terms = normalize(state.q).split(" ").filter(Boolean);
    var hits = 0;

    cards.forEach(function (card) {
      var hay = card.dataset.search || "";
      var tags = (card.dataset.tags || "").split("|");
      var okTag = !state.tag || tags.indexOf(state.tag) !== -1;
      var okQuery = terms.every(function (t) { return hay.indexOf(t) !== -1; });
      var show = okTag && okQuery;
      card.hidden = !show;
      if (show) hits++;
    });

    if (hitCount) hitCount.textContent = String(hits);
    if (noHit) noHit.hidden = hits !== 0;
    if (clearBtn) clearBtn.hidden = !state.q;

    tagBar && [].forEach.call(tagBar.querySelectorAll(".tag-chip"), function (chip) {
      chip.classList.toggle("is-on", (chip.dataset.tag || "") === state.tag);
    });

    if (pushUrl) {
      var params = new URLSearchParams();
      if (state.q) params.set("q", state.q);
      if (state.tag) params.set("tag", state.tag);
      var qs = params.toString();
      history.replaceState(null, "", qs ? "?" + qs : location.pathname);
    }
  }

  // 入力は少し待ってから反映(打つたびに走らせない)
  var timer = null;
  input.addEventListener("input", function () {
    clearTimeout(timer);
    timer = setTimeout(function () {
      state.q = input.value;
      apply(true);
    }, 140);
  });
  input.addEventListener("search", function () { state.q = input.value; apply(true); });

  clearBtn && clearBtn.addEventListener("click", function () {
    input.value = "";
    state.q = "";
    apply(true);
    input.focus();
  });

  tagBar && tagBar.addEventListener("click", function (e) {
    var chip = e.target.closest(".tag-chip");
    if (!chip) return;
    var tag = chip.dataset.tag || "";
    state.tag = state.tag === tag ? "" : tag;  // 同じタグをもう一度押したら解除
    apply(true);
  });

  // ページを開いた時点でURLの条件を復元する
  var params = new URLSearchParams(location.search);
  state.q = params.get("q") || "";
  state.tag = params.get("tag") || "";
  if (state.q) input.value = state.q;
  apply(false);

  // "/" キーで検索欄へ
  document.addEventListener("keydown", function (e) {
    if (e.key === "/" && document.activeElement !== input) {
      e.preventDefault();
      input.focus();
    }
  });
})();
