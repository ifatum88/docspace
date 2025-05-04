document.addEventListener('DOMContentLoaded', function () {
  const toggleBtn = document.getElementById('toggle-page-details');
  const closeBtn = document.getElementById('close-page-details');
  const panel = document.querySelector('.page-details');

  toggleBtn?.addEventListener('click', () => {
    panel.classList.remove('hidden');
    panel.classList.add('visible');
  });

  closeBtn?.addEventListener('click', () => {
    panel.classList.remove('visible');
    panel.classList.add('hidden');
  });
});