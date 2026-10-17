(() => {
  const root = document.documentElement;
  const languageButton = document.querySelector('[data-language-toggle]');
  const themeButton = document.querySelector('[data-theme-toggle]');
  const menuButton = document.querySelector('[data-menu-toggle]');
  const mobileMenu = document.querySelector('#mobile-menu');
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function setLocale(locale) {
    const lang = locale === 'en' ? 'en' : 'ar';
    root.lang = lang;
    root.dir = lang === 'ar' ? 'rtl' : 'ltr';
    document.querySelectorAll('[data-ar][data-en]').forEach((node) => {
      node.textContent = node.dataset[lang];
    });
    document.querySelectorAll('[data-ar-label][data-en-label]').forEach((node) => {
      node.setAttribute('aria-label', lang === 'ar' ? node.dataset.arLabel : node.dataset.enLabel);
    });
    if (languageButton) languageButton.textContent = lang === 'ar' ? 'EN' : 'ع';
    document.title = lang === 'ar'
      ? 'Ather Agents — فريقك البرمجي لـ OpenCode v2'
      : 'Ather Agents — Your OpenCode v2 agent team';
    try { localStorage.setItem('ather-language', lang); } catch (_) {}
  }

  let savedLanguage = 'ar';
  try { savedLanguage = localStorage.getItem('ather-language') || 'ar'; } catch (_) {}
  setLocale(savedLanguage);
  languageButton?.addEventListener('click', () => setLocale(root.lang === 'ar' ? 'en' : 'ar'));

  function setTheme(theme) {
    const next = theme === 'light' ? 'light' : 'dark';
    root.dataset.theme = next;
    const metaTheme = document.querySelector('meta[name="theme-color"]');
    if (metaTheme) metaTheme.content = next === 'dark' ? '#0B0D15' : '#F7F8FC';
    const glyph = document.querySelector('[data-theme-glyph]');
    if (glyph) glyph.textContent = next === 'dark' ? '◐' : '◑';
    try { localStorage.setItem('ather-theme', next); } catch (_) {}
  }
  themeButton?.addEventListener('click', () => setTheme(root.dataset.theme === 'dark' ? 'light' : 'dark'));

  menuButton?.addEventListener('click', () => {
    const open = menuButton.getAttribute('aria-expanded') !== 'true';
    menuButton.setAttribute('aria-expanded', String(open));
    mobileMenu.hidden = !open;
    const label = root.lang === 'ar'
      ? (open ? 'إغلاق القائمة' : 'فتح القائمة')
      : (open ? 'Close menu' : 'Open menu');
    menuButton.setAttribute('aria-label', label);
    menuButton.textContent = open ? '×' : '☰';
  });
  mobileMenu?.querySelectorAll('a').forEach((link) => link.addEventListener('click', () => {
    mobileMenu.hidden = true;
    menuButton?.setAttribute('aria-expanded', 'false');
  }));

  const installCommand = document.querySelector('[data-install-command]')?.textContent.trim() || '';
  const copyButton = document.querySelector('[data-copy-install]');
  const copyStatus = document.querySelector('[data-copy-status]');
  copyButton?.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(installCommand);
      copyStatus.textContent = root.lang === 'ar' ? 'تم نسخ الأمر.' : 'Command copied.';
    } catch (_) {
      const range = document.createRange();
      range.selectNodeContents(document.querySelector('[data-install-command]'));
      const selection = window.getSelection();
      selection.removeAllRanges();
      selection.addRange(range);
      copyStatus.textContent = root.lang === 'ar' ? 'حدّد الأمر وانسخه.' : 'Select the command and copy it.';
    }
  });

  const steps = window.gsap?.utils?.toArray('[data-step]') || Array.from(document.querySelectorAll('[data-step]'));
  let activeStep = 0;
  function showStep(next) {
    if (!steps.length) return;
    const wrapIndex = window.gsap?.utils ? window.gsap.utils.wrap(0, steps.length) : ((n) => (n + steps.length) % steps.length);
    activeStep = wrapIndex(next);
    steps.forEach((step, index) => {
      step.classList.toggle('is-active', index === activeStep);
      if (index === activeStep) step.setAttribute('aria-current', 'step');
      else step.removeAttribute('aria-current');
    });
    const counter = document.querySelector('[data-flow-counter]');
    if (counter) counter.textContent = `${String(activeStep + 1).padStart(2, '0')} — ${String(steps.length).padStart(2, '0')}`;
  }
  document.querySelector('[data-flow-next]')?.addEventListener('click', () => showStep(activeStep + 1));
  document.querySelector('[data-flow-prev]')?.addEventListener('click', () => showStep(activeStep - 1));

  document.querySelectorAll('[data-year]').forEach((node) => { node.textContent = new Date().getFullYear(); });
  if (reducedMotion || !window.gsap?.utils) return;

  const { gsap } = window;
  gsap.utils.toArray('.reveal').forEach((element) => {
    element.style.visibility = 'hidden';
    const observer = new IntersectionObserver((entries) => {
      if (!entries[0].isIntersecting) return;
      observer.disconnect();
      gsap.fromTo(element, { autoAlpha: 0, y: 14 }, { autoAlpha: 1, y: 0, duration: 0.55, ease: 'power2.out', clearProps: 'visibility' });
    }, { threshold: 0.12 });
    observer.observe(element);
  });

  const hero = document.querySelector('.hero');
  if (hero && window.matchMedia('(pointer: fine)').matches) {
    const clampPercent = gsap.utils.clamp(8, 92);
    const mapX = gsap.utils.mapRange(0, window.innerWidth, 8, 92);
    const mapY = gsap.utils.mapRange(0, window.innerHeight, 12, 82);
    let frame = 0;
    window.addEventListener('pointermove', (event) => {
      if (frame) cancelAnimationFrame(frame);
      frame = requestAnimationFrame(() => {
        hero.style.setProperty('--glow-x', `${clampPercent(mapX(event.clientX))}%`);
        hero.style.setProperty('--glow-y', `${clampPercent(mapY(event.clientY))}%`);
        frame = 0;
      });
    }, { passive: true });
  }
})();
