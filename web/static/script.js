// web/static/script.js

// Ждём, пока DOM полностью загрузится
document.addEventListener('DOMContentLoaded', function () {
  console.log('✅ DOM загружен, script.js работает');

  let USER_DATA = null;

  function navigateTo(screen) {
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    setTimeout(() => {
      document.querySelectorAll('.screen').forEach(s => s.style.display = 'none');
      const screenElement = document.getElementById(screen + '-screen');
      if (screenElement) {
        screenElement.style.display = 'flex';
        setTimeout(() => screenElement.classList.add('active'), 10);
      }
    }, 300);
  }

  function navigateBack() { navigateTo('dashboard'); }

  function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.querySelector('.overlay');
    if (sidebar && overlay) {
      sidebar.classList.toggle('open');
      overlay.classList.toggle('active');
    }
  }

  function openQRModal() {
    const modal = document.getElementById('qr-modal');
    if (modal) modal.style.display = 'flex';
  }

  function closeQRModal() {
    const modal = document.getElementById('qr-modal');
    if (modal) modal.style.display = 'none';
  }

  function setLang(lang) {
    alert('Язык изменён на: ' + lang);
  }

  function buyPremium() {
    alert("💳 Премиум скоро! Ожидайте интеграцию.");
  }

  // === Старт авторизации ===
  window.startAuth = function () {
    const urlParams = new URLSearchParams(window.location.search);
    const user_id = urlParams.get('user_id');
    const hash = urlParams.get('hash');

    if (!user_id || !hash) {
      alert('❌ Неверная ссылка. Откройте из бота.');
      return;
    }

    fetch(`/api/user/${user_id}`)
      .then(res => res.json())
      .then(data => {
        USER_DATA = data;

        // Безопасное обновление элементов
        const updateElement = (id, value) => {
          const el = document.getElementById(id);
          if (el) el.textContent = value;
        };

        updateElement('user-name', data.first_name);
        updateElement('user-username', data.username ? '@' + data.username : 'не указан');
        updateElement('user-id', data.id);
        updateElement('referrals', data.referrals);
        updateElement('premium-status', data.is_premium ? 'Премиум' : 'Базовая');

        const photo = document.getElementById('profile-photo');
        if (photo) {
          photo.textContent = data.first_name[0]?.toUpperCase() || '?';
        }

        const theme = data.theme || 'light';
        document.documentElement.setAttribute('data-theme', theme);

        navigateTo('dashboard');
      })
      .catch(err => {
        console.error('❌ Ошибка загрузки данных:', err);
        alert('❌ Ошибка: не удалось загрузить данные');
      });
  };

  // === Оффлайн-бар ===
  const offlineBar = document.getElementById('offline-bar');
  if (offlineBar) {
    window.addEventListener('offline', () => offlineBar.style.display = 'block');
    window.addEventListener('online',  () => offlineBar.style.display = 'none');
    if (!navigator.onLine) offlineBar.style.display = 'block';
  }

  console.log('✅ startAuth доступна глобально');
});
