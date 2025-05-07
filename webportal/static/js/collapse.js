document.addEventListener('click', function(event) {
  const toggler = event.target.closest('[data-toggle="collapse"]');
  if (!toggler) return;

  const targetSelector = toggler.dataset.target;
  const defaultText = toggler.dataset.text || 'Показать';
  const altText = toggler.dataset.altText || 'Скрыть';

  const target = document.querySelector(targetSelector);
  if (!target) {
    console.warn('Collapse target not found:', targetSelector);
    return;
  }

  const isVisible = target.style.display === 'block';
  target.style.display = isVisible ? 'none' : 'block';
  toggler.textContent = isVisible ? defaultText : altText;
});