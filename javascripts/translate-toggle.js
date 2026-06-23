document$.subscribe(() => {
  const t = document.body.textContent;
  const cjk = (t.match(/[一-鿿㐀-䶿]/g) || []).length;
  document.documentElement.lang = cjk / t.length > 0.3 ? 'zh' : 'en';
});
