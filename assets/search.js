import Fuse from '{{ "fuse.min.mjs" | relURL }}'

{{ $searchDataFile := printf "%s.search-data.json" .Language.Name }}
{{ $searchData := resources.Get "search-data.json" | resources.ExecuteAsTemplate $searchDataFile . | resources.Minify | resources.Fingerprint }}
{{ $searchConfig := i18n "bookSearchConfig" | default "{}" }}

(function () {
  const searchDataURL = '{{ partial "docs/links/resource-precache" $searchData }}';
  const indexConfig = Object.assign({{ $searchConfig }}, {
    includeScore: true,
    useExtendedSearch: true,
    fieldNormWeight: 1.5,
    threshold: 0.2,
    ignoreLocation: true,
    keys: [
      {
        name: 'title',
        weight: 0.7
      },
      {
        name: 'content',
        weight: 0.3
      }
    ]
  });

  const input = document.querySelector('#book-search-input');
  const results = document.querySelector('#book-search-results');

  if (!input) {
    return
  }

  input.addEventListener('focus', init);
  input.addEventListener('keyup', search);

  document.addEventListener('keydown', focusOnKeyDown);

  function focusOnKeyDown(event) {
    if (event.key === 'k' && (event.metaKey || event.ctrlKey)) {
      event.preventDefault();
      input.focus();
      return;
    }
    if (input === document.activeElement) {
      return;
    }
    if (event.target.value !== undefined) {
      return;
    }
    if (event.key === '/') {
      event.preventDefault();
      input.focus();
    }
  }

  function init() {
    input.removeEventListener('focus', init);
    input.required = true;
    fetch(searchDataURL)
      .then(pages => pages.json())
      .then(pages => {
        window.bookSearchIndex = new Fuse(pages, indexConfig);
      })
      .then(() => input.required = false)
      .then(search);
  }

  function search() {
    while (results.firstChild) {
      results.removeChild(results.firstChild);
    }
    if (!input.value) {
      return;
    }
    const searchHits = window.bookSearchIndex.search(input.value).slice(0,10);
    searchHits.forEach(function (page) {
      const li = element('<li><a href></a><small></small><p></p></li>');
      const a = li.querySelector('a'), small = li.querySelector('small'), p = li.querySelector('p');
      a.href = page.item.href;
      a.textContent = page.item.title;
      small.textContent = page.item.section;
      var content = page.item.content || '';
      p.textContent = content.substring(0, 100).replace(/\s+/g, ' ') + (content.length > 100 ? '…' : '');
      results.appendChild(li);
    });
  }

  function element(content) {
    const div = document.createElement('div');
    div.innerHTML = content;
    return div.firstChild;
  }
})();
