// 認可サーバのつもりの最小サイト (依存なし)
// node server.js  → http://127.0.0.1:8863
const http = require('http');
const PORT = 8863;

function page(user) {
  const status = user ? 'LOGGED_IN ' + user : 'ANON';
  return `<!doctype html><meta charset="utf-8"><title>idp</title>
<h1 id="status">${status}</h1>
<form method="POST" action="/login">
<input id="u" name="u" autocomplete="off">
<input id="p" name="p" type="password" autocomplete="off">
<button id="go" type="submit">login</button>
</form>
<p id="ls"></p>
<script>
  // 初回だけランダムな印を保存する(同じ値=同じ保存領域)
  if (!localStorage.getItem('tag')) {
    localStorage.setItem('tag', Math.random().toString(36).slice(2, 8));
  }
  document.getElementById('ls').textContent =
    'localStorage.tag=' + localStorage.getItem('tag');
</script>`;
}

http.createServer((req, res) => {
  const cookie = req.headers.cookie || '';
  const m = /(?:^|; )sid=([^;]+)/.exec(cookie);
  const user = m ? decodeURIComponent(m[1]) : null;

  if (req.method === 'POST' && req.url === '/login') {
    let body = '';
    req.on('data', c => body += c);
    req.on('end', () => {
      const p = new URLSearchParams(body);
      const u = p.get('u') || 'anon';
      res.writeHead(302, {
        'Set-Cookie': [
          'sid=' + encodeURIComponent(u) + '; Path=/; HttpOnly; Max-Age=86400',
          'theme=dark; Path=/; Max-Age=86400'
        ],
        'Location': '/'
      });
      res.end();
    });
    return;
  }
  res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
  res.end(page(user));
}).listen(PORT, '127.0.0.1', () => console.log('listening ' + PORT));
