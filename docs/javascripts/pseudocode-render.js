// Render all pseudocode blocks on page load / navigation
document$.subscribe(() => {
  document.querySelectorAll('pre.pseudocode').forEach(el => {
    try {
      pseudocode.renderElement(el);
    } catch(e) {
      console.error('Pseudocode render error:', e);
    }
  });
});
