// Смена темы
function toggleTheme() {
  const html = document.documentElement;
  const isDark = html.getAttribute('data-theme') === 'dark';
  const newTheme = isDark ? 'light' : 'dark';
  html.setAttribute('data-theme', newTheme);
  document.getElementById('theme-icon').textContent = isDark ? 'light_mode' : 'dark_mode';
  localStorage.setItem('theme', newTheme);
  
  // ✅ ДОБАВЛЕНО: сохраняем тему в куки
  document.cookie = `theme=${newTheme}; path=/; max-age=31536000`; // 1 год
}

// Скрытие шапки при скролле
let lastScroll = 0;
window.addEventListener('scroll', () => {
  const current = window.scrollY;
  const header = document.getElementById('combined-header');
  if (!header) return;

  if (current > 100 && current > lastScroll) {
    header.classList.add('hidden');
  } else if (current < lastScroll && current > 50) {
    header.classList.remove('hidden');
  }

  lastScroll = current;
});

// Toast
window.Toast = {
  show: (msg) => {
    const toast = document.getElementById('toast');
    toast.textContent = msg;
    toast.className = 'toast show';
    setTimeout(() => {
      toast.className = 'toast';
    }, 3000);
  },
  info: (msg) => Toast.show(msg),
  success: (msg) => Toast.show(msg),
  warning: (msg) => Toast.show(msg),
  error: (msg) => Toast.show(msg)
};

// Инициализация
document.addEventListener('DOMContentLoaded', () => {
  // ✅ ПРИОРИТЕТ: сначала cookie, потом localStorage
  const savedTheme = 
    document.cookie.match(/theme=([^;]+)/)?.[1] || 
    localStorage.getItem('theme') || 
    'light';

  document.documentElement.setAttribute('data-theme', savedTheme);
  const icon = document.getElementById('theme-icon');
  if (icon) {
    icon.textContent = savedTheme === 'dark' ? 'light_mode' : 'dark_mode';
  }

  if (window.Telegram?.WebApp) {
    window.Telegram.WebApp.ready();
  }
});