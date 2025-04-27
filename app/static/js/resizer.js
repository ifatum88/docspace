document.addEventListener('DOMContentLoaded', () => {
  const rootStyles = getComputedStyle(document.documentElement);

  const sidebarWidth = parseInt(rootStyles.getPropertyValue('--sidebar-width')); // 200
  const sidebarMinWidth = parseInt(rootStyles.getPropertyValue('--sidebar-width-min')); // 180
  const sidebarMaxWidth = parseInt(rootStyles.getPropertyValue('--sidebar-width-max')); // 400
  const sidebarCollapsedWidth = parseInt(rootStyles.getPropertyValue('--sidebar-width-collapsed')); // 60

  const resizer = document.getElementById('resizer');
  const sidebar = document.getElementById('sidebar');
  const main = document.getElementById('main');
  const toggleBtn = document.getElementById('toggle-sidebar');
  

  const collapsedWidth = sidebarCollapsedWidth;

  // 💾 Загружаем сохраненные значения из localStorage
  const savedCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
  let savedWidth = parseInt(localStorage.getItem('sidebarWidth'));
  if (isNaN(savedWidth)) {
    savedWidth = sidebarWidth; // дефолтная ширина
  }

  let lastSidebarWidth = savedWidth;

  // 📦 Устанавливаем начальное состояние
  if (savedCollapsed) {
    document.documentElement.classList.add('sidebar-collapsed');
    sidebar.style.width = `${collapsedWidth}px`;
    resizer.style.left = `${collapsedWidth}px`;
    main.style.marginLeft = `${collapsedWidth + 5}px`;
    if (toggleBtn) toggleBtn.title = "Развернуть панель";
  } else {
    document.documentElement.classList.remove('sidebar-collapsed');
    sidebar.style.width = `${savedWidth}px`;
    resizer.style.left = `${savedWidth}px`;
    main.style.marginLeft = `${savedWidth + 5}px`;
    if (toggleBtn) toggleBtn.title = "Свернуть панель";
  }

  // 🖱️ Ресайз панели мышкой (drag & drop)
  resizer.addEventListener('mousedown', (e) => {
    if (document.documentElement.classList.contains('sidebar-collapsed')) return; // нельзя ресайзить, если панель свернута

    document.body.style.userSelect = 'none';
    sidebar.classList.add('no-transition');
    main.classList.add('no-transition');
    resizer.classList.add('no-transition');

    const onMouseMove = (e) => {
      const newWidth = Math.min(Math.max(e.clientX, sidebarMinWidth), sidebarMaxWidth);
      lastSidebarWidth = newWidth;
      sidebar.style.width = `${newWidth}px`;
      resizer.style.left = `${newWidth}px`;
      main.style.marginLeft = `${newWidth + 5}px`;
    };

    const onMouseUp = () => {
      document.removeEventListener('mousemove', onMouseMove);
      document.removeEventListener('mouseup', onMouseUp);
      document.body.style.userSelect = 'auto';

      sidebar.classList.remove('no-transition');
      main.classList.remove('no-transition');
      resizer.classList.remove('no-transition');

      // 💾 Сохраняем ширину после ресайза
      localStorage.setItem('sidebarWidth', lastSidebarWidth);
    };

    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', onMouseUp);
  });

  // 🎛️ Кнопка свернуть/развернуть панель
  toggleBtn?.addEventListener('click', () => {
    const isCollapsed = document.documentElement.classList.toggle('sidebar-collapsed');

    if (isCollapsed) {
      // Панель свернута
      sidebar.style.width = `${collapsedWidth}px`;
      resizer.style.left = `${collapsedWidth}px`;
      main.style.marginLeft = `${collapsedWidth + 5}px`;
      toggleBtn.title = "Развернуть панель";
    } else {
      // Панель развернута
      sidebar.style.width = `${lastSidebarWidth}px`;
      resizer.style.left = `${lastSidebarWidth}px`;
      main.style.marginLeft = `${lastSidebarWidth + 5}px`;
      toggleBtn.title = "Свернуть панель";
    }

    // 💾 Сохраняем состояние
    localStorage.setItem('sidebarCollapsed', isCollapsed ? 'true' : 'false');
    localStorage.setItem('sidebarWidth', lastSidebarWidth);
  });
});