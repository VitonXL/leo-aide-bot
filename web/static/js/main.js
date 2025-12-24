// === СМЕНА ТЕМЫ ===
function toggleTheme() {
  const html = document.documentElement;
  const isDark = html.getAttribute('data-theme') === 'dark';
  const newTheme = isDark ? 'light' : 'dark';
  
  // Устанавливаем тему
  html.setAttribute('data-theme', newTheme);
  
  // Меняем иконку (Material Icons)
  const themeIcon = document.getElementById('theme-icon');
  if (themeIcon) {
    themeIcon.textContent = isDark ? 'light_mode' : 'dark_mode';
  }

  // Сохраняем
  localStorage.setItem('theme', newTheme);
  document.cookie = `theme=${newTheme}; path=/; max-age=31536000`; // 1 год
}

// === СКРЫТИЕ ШАПКИ ПРИ СКРОЛЛЕ ===
let lastScroll = 0;
const header = document.getElementById('combined-header');
if (header) {
  window.addEventListener('scroll', () => {
    const current = window.scrollY;

    if (current > 100 && current > lastScroll) {
      // Скрываем шапку при скролле вниз
      header.classList.add('hidden');
    } else if (current < lastScroll && current > 50) {
      // Показываем при скролле вверх
      header.classList.remove('hidden');
    }

    lastScroll = current;
  });
}

// === TOAST УВЕДОМЛЕНИЯ ===
window.Toast = {
  show: (msg, type = 'info') => {
    const toast = document.getElementById('toast');
    if (!toast) return;

    toast.textContent = msg;
    toast.className = `toast show ${type}`;
    
    setTimeout(() => {
      toast.className = 'toast';
    }, 3000);
  },
  info: (msg) => Toast.show(msg, 'info'),
  success: (msg) => Toast.show(msg, 'success'),
  warning: (msg) => Toast.show(msg, 'warning'),
  error: (msg) => Toast.show(msg, 'error')
};

// === ИНИЦИАЛИЗАЦИЯ ПРИ ЗАГРУЗКЕ ===
document.addEventListener('DOMContentLoaded', () => {
  // Приоритет: cookie → localStorage → default ('light')
  const savedTheme = 
    document.cookie.match(/theme=([^;]+)/)?.[1] || 
    localStorage.getItem('theme') || 
    'light';

  // Устанавливаем тему
  document.documentElement.setAttribute('data-theme', savedTheme);

  // Обновляем иконку
  const themeIcon = document.getElementById('theme-icon');
  if (themeIcon) {
    themeIcon.textContent = savedTheme === 'dark' ? 'light_mode' : 'dark_mode';
  }

  // Инициализация Telegram Web App
  if (window.Telegram?.WebApp) {
    window.Telegram.WebApp.ready();
    window.Telegram.WebApp.expand();
  }
});