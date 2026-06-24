document$.subscribe(() => {
  document.querySelectorAll("pre.pseudocode").forEach(el => pseudocode.renderElement(el));
});
