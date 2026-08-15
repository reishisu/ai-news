// 日本語(全角)を2文字ぶんとして数えて桁を揃える
const width = s => [...s].reduce((n, c) => n + (/[ᄀ-ᅟ⺀-꓏가-힣豈-﫿︰-﹯＀-｠￠-￦]/.test(c) ? 2 : 1), 0);
const pad = (s, w) => s + ' '.repeat(Math.max(0, w - width(s)));
module.exports = { width, pad };
