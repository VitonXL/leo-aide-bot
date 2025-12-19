// web/static/js/admin.js

let statsData = {};
let usersList = [];
let currentChart = null; // Для уничтожения предыдущего графика

document.addEventListener('DOMContentLoaded', async () => {
  console.log('✅ admin.js: загружен');

  await loadStats();
  await loadUsersList();
  changeViewMode('cards'); // По умолчанию
});

// === Загрузка статистики ===
async function loadStats() {
  try {
    const res = await fetch('/api/admin/stats');
    statsData = await res.json();

    updateStatsDisplay();
  } catch (e) {
    console.error('❌ Ошибка загрузки статистики:', e);
    document.getElementById('stats-container').innerHTML = '<p class="text-danger">Не удалось загрузить данные</p>';
  }
}

// === Загрузка списка пользователей ===
async function loadUsersList() {
  try {
    const res = await fetch('/api/admin/users');
    usersList = await res.json();

    const tbody = document.getElementById('users-table-body');
    if (tbody) {
      tbody.innerHTML = usersList.map(u => `
        <tr>
          <td>${u.id}</td>
          <td>${u.first_name || '—'}</td>
          <td>@${u.username || '—'}</td>
          <td><span class="badge bg-${u.role === 'admin' ? 'danger' : u.role === 'premium' ? 'success' : 'secondary'}">${u.role}</span></td>
          <td>${u.language || 'ru'}</td>
          <td>${u.premium_expires ? new Date(u.premium_expires).toLocaleDateString() : '—'}</td>
          <td>${new Date(u.last_seen).toLocaleString()}</td>
          <td>
            <button class="btn btn-sm btn-outline-primary" onclick="inspectUser(${u.id})">👁️</button>
          </td>
        </tr>
      `).join('');
    }
  } catch (e) {
    console.error('❌ Ошибка загрузки пользователей:', e);
  }
}

// === Обновление отображения в текущем режиме ===
function updateStatsDisplay() {
  const mode = document.getElementById('view-mode').value;
  changeViewMode(mode);
}

// === Переключение режимов ===
function changeViewMode(mode) {
  const container = document.getElementById('stats-container');

  // Уничтожаем предыдущий график
  if (currentChart) {
    currentChart.destroy();
    currentChart = null;
  }

  // Скрываем таблицу
  const usersTable = document.getElementById('users-table-container');
  if (usersTable) usersTable.classList.add('d-none');

  if (mode === 'cards') {
    renderStatsCards();
  } else if (mode === 'table') {
    renderStatsTable();
  } else if (mode === 'chart') {
    renderActivityChart();
  } else if (mode === 'bars') {
    renderCommandsChart();
  }
}

function renderStatsCards() {
  document.getElementById('users-table-container').classList.add('d-none');
  const container = document.getElementById('stats-container');
  container.innerHTML = `
    <div class="row g-3">
      <div class="col-md-3">
        <div class="stat-card bg-primary text-white">
          <h4>${statsData.total_users || 0}</h4>
          <p>Всего пользователей</p>
        </div>
      </div>
      <div class="col-md-3">
        <div class="stat-card bg-success text-white">
          <h4>${statsData.premium_users || 0}</h4>
          <p>Премиум</p>
        </div>
      </div>
      <div class="col-md-3">
        <div class="stat-card bg-info text-white">
          <h4>${statsData.active_today || 0}</h4>
          <p>Активно сегодня</p>
        </div>
      </div>
      <div class="col-md-3">
        <div class="stat-card bg-warning text-dark">
          <h4>${statsData.referrals_count || 0}</h4>
          <p>Рефералов</p>
        </div>
      </div>
    </div>
  `;
}

function renderStatsTable() {
  document.getElementById('users-table-container').classList.add('d-none');
  document.getElementById('stats-container').innerHTML = `
    <table class="table table-bordered">
      <tr><td><strong>Пользователи</strong></td><td>${statsData.total_users || 0}</td></tr>
      <tr><td><strong>Премиум</strong></td><td>${statsData.premium_users || 0}</td></tr>
      <tr><td><strong>Активно сегодня</strong></td><td>${statsData.active_today || 0}</td></tr>
      <tr><td><strong>Рефералы</strong></td><td>${statsData.referrals_count || 0}</td></tr>
    </table>
  `;
}

function renderActivityChart() {
  document.getElementById('users-table-container').classList.add('d-none');
  document.getElementById('stats-container').innerHTML = '<canvas id="activityChart"></canvas>';

  fetch('/api/admin/activity-by-day')
    .then(res => res.json())
    .then(data => {
      const ctx = document.getElementById('activityChart').getContext('2d');
      currentChart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: data.dates,
          datasets: [{
            label: 'Активность (по дням)',
            data: data.counts,
            borderColor: '#4CAF50',
            backgroundColor: 'rgba(76, 175, 80, 0.1)',
            fill: true,
            tension: 0.3
          }]
        },
        options: {
          responsive: true,
          plugins: {
            legend: { display: true }
          }
        }
      });
    })
    .catch(e => {
      document.getElementById('stats-container').innerHTML = '<p class="text-danger">Ошибка графика активности</p>';
      console.error(e);
    });
}

function renderCommandsChart() {
  document.getElementById('users-table-container').classList.add('d-none');
  document.getElementById('stats-container').innerHTML = '<canvas id="commandsChart"></canvas>';

  fetch('/api/admin/top-commands')
    .then(res => res.json())
    .then(data => {
      const ctx = document.getElementById('commandsChart').getContext('2d');
      currentChart = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: data.commands,
          datasets: [{
            label: 'Количество использований',
            data: data.counts,
            backgroundColor: '#66BB6A'
          }]
        },
        options: {
          responsive: true,
          indexAxis: 'y'
        }
      });
    })
    .catch(e => {
      document.getElementById('stats-container').innerHTML = '<p class="text-danger">Ошибка столбчатого графика</p>';
      console.error(e);
    });
}

// === Управление пользователями ===
async function searchUser() {
  const input = document.getElementById('search-user').value.trim();
  if (!input) return;

  try {
    const res = await fetch(`/api/admin/user?query=${encodeURIComponent(input)}`);
    const user = await res.json();

    if (user) {
      document.getElementById('found-user').textContent = `@${user.username} (ID: ${user.id})`;
      document.getElementById('user-actions').style.display = 'block';
      window.currentFoundUser = user;
    } else {
      alert('Пользователь не найден');
    }
  } catch (e) {
    alert('Ошибка поиска');
  }
}

async function grantPremium() {
  if (!window.currentFoundUser) return;

  if (!confirm(`Выдать премиум ${window.currentFoundUser.first_name}?`)) return;

  await fetch('/api/admin/grant-premium', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: window.currentFoundUser.id })
  });

  alert('✅ Премиум выдан на 30 дней');
}

function blockUser() {
  alert('Функция в разработке');
}

function resetUser() {
  alert('Функция в разработке');
}

function inspectUser(userId) {
  alert(`Инспекция пользователя: ${userId}`);
}