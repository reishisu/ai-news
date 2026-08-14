// AIニュース デイリーダイジェスト — トップページ(プレースホルダー)用スクリプト
(function () {
  var PAGE_URL = "https://reishisu.github.io/ai-news/";
  var TITLE = "AIニュース デイリーダイジェスト";
  var u = encodeURIComponent(PAGE_URL), t = encodeURIComponent(TITLE);

  document.getElementById("sh-x").href = "https://twitter.com/intent/tweet?text=" + t + "&url=" + u;
  document.getElementById("sh-line").href = "https://social-plugins.line.me/lineit/share?url=" + u;
  document.getElementById("sh-fb").href = "https://www.facebook.com/sharer/sharer.php?u=" + u;
  document.getElementById("sh-hatena").href = "https://b.hatena.ne.jp/entry/panel/?url=" + u + "&btitle=" + t;

  document.getElementById("sh-copy").addEventListener("click", function () {
    var label = document.getElementById("copyLabel");
    (navigator.clipboard ? navigator.clipboard.writeText(PAGE_URL) : Promise.reject())
      .then(function () { label.textContent = "コピーしました ✓"; })
      .catch(function () { window.prompt("このURLをコピーしてください", PAGE_URL); })
      .finally(function () { setTimeout(function () { label.textContent = "リンクをコピー"; }, 2000); });
  });

  var nativeBtn = document.getElementById("sh-native");
  if (navigator.share) {
    nativeBtn.hidden = false;
    nativeBtn.addEventListener("click", function () {
      navigator.share({ title: TITLE, url: PAGE_URL }).catch(function () {});
    });
  }
})();
