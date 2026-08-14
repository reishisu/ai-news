// AIニュース デイリーダイジェスト — SNS共有フローティングバー(_build_index.py が注入)
(function () {
  var bar = document.getElementById("ai-news-sharebar");
  if (!bar) return;
  var toggle = bar.querySelector(".sb-toggle");
  var toast = bar.querySelector(".sb-toast");
  var url = location.href.split("#")[0];
  var title = document.title || "AIニュース デイリーダイジェスト";
  var u = encodeURIComponent(url), t = encodeURIComponent(title);
  var links = {
    x: "https://twitter.com/intent/tweet?text=" + t + "&url=" + u,
    line: "https://social-plugins.line.me/lineit/share?url=" + u,
    fb: "https://www.facebook.com/sharer/sharer.php?u=" + u,
    hatena: "https://b.hatena.ne.jp/entry/panel/?url=" + u + "&btitle=" + t
  };
  bar.querySelectorAll("[data-share]").forEach(function (el) {
    var kind = el.getAttribute("data-share");
    if (links[kind]) el.href = links[kind];
  });
  function showToast(msg) {
    toast.textContent = msg;
    toast.classList.add("show");
    setTimeout(function () { toast.classList.remove("show"); }, 2000);
  }
  bar.querySelector('[data-share="copy"]').addEventListener("click", function () {
    (navigator.clipboard ? navigator.clipboard.writeText(url) : Promise.reject())
      .then(function () { showToast("リンクをコピーしました ✓"); })
      .catch(function () { window.prompt("このURLをコピーしてください", url); });
  });
  toggle.addEventListener("click", function () {
    if (navigator.share && !bar.classList.contains("open")) {
      navigator.share({ title: title, url: url }).catch(function () {
        bar.classList.add("open");
        toggle.setAttribute("aria-expanded", "true");
      });
      return;
    }
    var open = bar.classList.toggle("open");
    toggle.setAttribute("aria-expanded", String(open));
  });
})();
