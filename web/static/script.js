// web/static/script.js

// === Глобальные переменные ===
let USER_DATA = null;

// === Навигация между экранами ===
function navigateTo(screen) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  setTimeout(() => {
    document.querySelectorAll('.screen').forEach(s => s.style.display = 'none');
    document.getElementById(screen + '-screen').style.display = 'flex';
    setTimeout(() => document.getElementById(screen + '-screen').classList.add('active'), 10);
  }, 300);
}

function navigateBack() { navigateTo('dashboard'); }

// === Старт авторизации ===
function startAuth() {
  const urlParams = new URLSearchParams(window.location.search);
  const user_id = urlParams.get('user_id');
  const hash = urlParams.get('hash');

  if (!user_id || !hash) {
    alert('❌ Неверная ссылка. Пожалуйста, перейдите из бота.');
    return;
  }

  // Проверяем подпись
  fetch(`/api/user/${user_id}`)
    .then(res => res.json())
    .then(data => {
      USER_DATA = data;
      document.getElementById('user-name').textContent = data.first_name;
      document.getElementById('user-username').textContent = data.username ? '@' + data.username : 'не указан';
      document.getElementById('user-id').textContent = data.id;
      document.getElementById('referrals').textContent = data.referrals;
      document.getElementById('profile-photo').textContent = data.first_name[0]?.toUpperCase() || '?';

      // Тема
      const theme = data.theme || 'light';
      document.documentElement.setAttribute('data-theme', theme);
      document.getElementById('current-theme').textContent = theme === 'light' ? 'Светлая' : 'Тёмкая';

      // Подписка
      document.getElementById('premium-status').textContent = data.is_premium ? 'Премиум' : 'Базовая';
      document.getElementById('premium-status').style.color = data.is_premium ? '#DAA520' : '#333';

      // Переход
      navigateTo('dashboard');
    })
    .catch(err => {
      console.error(err);
      alert('❌ Ошибка загрузки данных');
    });
}

// === Смена темы ===
function toggleTheme() {
  const currentTheme = document.documentElement.getAttribute('data-theme');
  const newTheme = currentTheme === 'light' ? 'dark' : 'light';
  document.documentElement.setAttribute('data-theme', newTheme);
  document.getElementById('current-theme').textContent = newTheme === 'light' ? 'Светлая' : 'Тёмкая';

  // В куку
  document.cookie = `theme=${newTheme}; path=/; max-age=31536000`;

  // В БД
  const urlParams = new URLSearchParams(window.location.search);
  const user_id = urlParams.get('user_id');
  const hash = urlParams.get('hash');

  if (user_id && hash) {
    fetch('/api/set-theme', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: +user_id, theme: newTheme, hash })
    }).catch(console.warn);
  }
}

// === Добавляем кнопку "Сменить тему" ===
document.addEventListener('DOMContentLoaded', () => {
  const profileMain = document.querySelector('.profile-main');
  const themeBtn = document.createElement('button');
  themeBtn.className = 'btn primary';
  themeBtn.style.marginTop = '20px';
  themeBtn.textContent = '🌙 Сменить тему';
  themeBtn.onclick = toggleTheme;
  profileMain.appendChild(themeBtn);

  // Если уже есть user_id — можно сразу стартовать (для тестов)
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.get('auto') === '1') {
    startAuth();
  }
});

// === Прочие функции ===
function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  const overlay = document.querySelector('.overlay');
  sidebar.classList.toggle('open');
  overlay.classList.toggle('active');
}

function openQRModal() { document.getElementById('qr-modal').style.display = 'flex'; }
function closeQRModal() { document.getElementById('qr-modal').style.display = 'none'; }

function setLang(lang) {
  alert(`Язык: ${lang}. Функция в разработке.`);
}

function buyPremium() {
  alert("💳 Премиум скоро! Ожидайте интеграцию.");
}

// === Оффлайн ===
const offlineBar = document.getElementById('offline-bar');
window.addEventListener('offline', () => offlineBar.style.display = 'block');
window.addEventListener('online', () => offlineBar.style.display = 'none');
window.onload = () => { if (!navigator.onLine) offlineBar.style.display = 'block'; };
