// 修复 navigation.footer 的线性跳转问题：
// 如果 prev/next 目标不在当前页面的目录分支内，改指向上级 index.html
document$.subscribe(() => {
  const prev = document.querySelector('.md-footer__link--prev')
  const next = document.querySelector('.md-footer__link--next')

  function fix(link) {
    if (!link) return
    const cur = window.location.pathname.replace(/\/$/, '').split('/').filter(Boolean)
    const tgt = new URL(link.href).pathname.replace(/\/$/, '').split('/').filter(Boolean)
    const scope = cur.length - 1
    let common = 0
    while (common < scope && common < tgt.length && cur[common] === tgt[common]) common++
    if (common < scope) {
      const isIndex = cur[cur.length - 1] === 'index.html'
      const parentDepth = isIndex ? scope - 1 : scope
      const parent = '/' + cur.slice(0, parentDepth).join('/') + '/index.html'
      link.href = parent
    }
  }

  fix(prev)
  fix(next)
})
