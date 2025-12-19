// web/static/js/admin.js

document.addEventListener('DOMContentLoaded', function () {
  console.log('✅ admin.js загружен');

  // Загружаем статистику
  loadStats();
  loadReviews();
  loadAds();

  // Устанавливаем режим по умолчанию
  changeViewMode('cards');
});

async function loadStats() {
  try {
    const res = await fetch('/api/admin/stats');
    const data = await res.json();

    document.getElementById('total-users').textContent = data.total_users;
    document.getElementById('premium-users').textContent = data.premium_users;
    document.getElementById('active-today').textContent = data.active_today;
  } catch (e) {
    console.error('❌ Ошибка загрузки статистики:', e);
  }
}

async function loadReviews() {
  try {
    const res = await fetch('/api/admin/reviews');
    const reviews = await res.json();
    const list = document.getElementById('reviews-list');
    list.innerHTML = '';

    reviews.forEach(r => {
      const el = document.createElement('div');
      el.style = 'padding: 12px; border-bottom: 1px solid var(--border);';
      el.innerHTML = `
        <p><strong>@${r.username || 'unknown'}</strong> (${r.date})</p>
        <p>${r.text}</p>
        <button onclick="deleteReview(${r.id})" style="background: #DD3935; color: white; border: none; padding: 6px 12px; border-radius: 4px;">Удалить</button>
      `;
      list.appendChild(el);
    });
  } catch (e) {
    console.error('❌ Ошибка загрузки отзывов:', e);
  }
}

async function loadAds() {
  // Заглушка
  document.getElementById('ads-list').innerHTML = '<p>🛠 Реклама — в разработке</p>';
}

async function searchUser() {
  const input = document.getElementById('search-user').value;
  try {
    const res = await fetch(`/api/admin/user?query=${input}`);
    const user = await res.json();
    if (user) {
      document.getElementById('found-user').textContent = `@${user.username} (ID: ${user.id})`;
      document.getElementById('user-actions').style.display = 'block';
    } else {
      alert('Пользователь не найден');
    }
  } catch (e) {
    alert('Ошибка');
  }
}

async function grantPremium() {
  const input = document.getElementById('search-user').value;
  if (!input) return;

  const confirmed = confirm('Выдать премиум этому пользователю?');
  if (!confirmed) return;

  try {
    await fetch('/api/admin/grant-premium', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: input })
    });
    alert('✅ Премиум выдан');
  } catch (e) {
    alert('❌ Ошибка');
  }
}

async function blockUser() {
  // Реализуется
}

async function deleteReview(id) {
  // Реализуется
}

function changeViewMode(mode) {
  const container = document.getElementById('stats-container');
  container.className = 'view-' + mode;
  // Здесь можно подгружать график через Chart.js и т.д.
}