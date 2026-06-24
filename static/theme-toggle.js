// 白天/黑夜模式切换
(() => {
  const KEY = 'book-theme'
  const btn = document.getElementById('theme-toggle')
  if (!btn) return

  const icon = btn.querySelector('.theme-icon')

  function setTheme(t) {
    document.documentElement.dataset.theme = t
    document.documentElement.style.colorScheme = t
    localStorage.setItem(KEY, t)
    if (icon) icon.textContent = t === 'dark' ? '☀️' : '🌙'
  }

  // 初始化：localStorage > 系统偏好
  const saved = localStorage.getItem(KEY)
  if (saved) {
    setTheme(saved)
  } else {
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    setTheme(prefersDark ? 'dark' : 'light')
  }

  btn.addEventListener('click', () => {
    const cur = document.documentElement.dataset.theme
    setTheme(cur === 'dark' ? 'light' : 'dark')
  })
})()
