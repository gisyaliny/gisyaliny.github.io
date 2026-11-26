'use strict';
(() => {
  const header = document.querySelector('.masthead');
  const toggle = header.querySelector('.menu-toggle');
  const nav = header.querySelector('nav');
  const compact = matchMedia('(max-width: 980px)');
  const anchors = [...nav.querySelectorAll('a[href^="#"]')];
  const sections = anchors.map(link => ({ link, section: document.querySelector(link.hash) }))
    .sort((a, b) => a.section.compareDocumentPosition(b.section) & Node.DOCUMENT_POSITION_FOLLOWING ? -1 : 1);
  function closeMenu(returnFocus = false) {
    toggle.setAttribute('aria-expanded', 'false');
    if (returnFocus) toggle.focus();
  }
  function syncLayout() {
    toggle.hidden = !compact.matches;
    closeMenu();
  }
  header.classList.add('enhanced');
  syncLayout();
  compact.addEventListener('change', syncLayout);
  toggle.addEventListener('click', () => {
    toggle.setAttribute('aria-expanded', String(toggle.getAttribute('aria-expanded') !== 'true'));
  });
  document.addEventListener('click', event => {
    if (!header.contains(event.target) || event.target.closest('a')) closeMenu();
  });
  header.addEventListener('focusout', event => {
    if (!header.contains(event.relatedTarget)) closeMenu();
  });
  header.addEventListener('keydown', event => {
    if (event.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') closeMenu(true);
  });
  let frame = 0;
  function update() {
    frame = 0;
    header.classList.toggle('scrolled', window.scrollY > 40);
    const threshold = header.getBoundingClientRect().bottom + 24;
    let selected;
    for (const item of sections) {
      if (item.section.getBoundingClientRect().top <= threshold) selected = item.link;
    }
    if (window.scrollY + innerHeight >= document.documentElement.scrollHeight - 3) selected = sections.at(-1).link;
    for (const link of anchors) {
      if (link === selected) link.setAttribute('aria-current','location');
      else link.removeAttribute('aria-current');
    }
  }
  function schedule() { if (!frame) frame = requestAnimationFrame(update); }
  addEventListener('scroll', schedule, {passive:true});
  addEventListener('resize', schedule);
  addEventListener('pageshow', schedule);
  update();
})();
