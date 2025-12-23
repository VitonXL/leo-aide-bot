// web/static/js/app.js

// Инициализация Telegram WebApp
document.addEventListener("DOMContentLoaded", () => {
    console.log("✅ DOM загружен");

    // Приветствие
    function updateGreeting() {
        const now = new Date();
        const hour = now.getHours();
        const greetingText = document.getElementById('greeting-text');
        const greetingIcon = document.getElementById('greeting-icon');

        if (hour >= 6 && hour < 12) {
            greetingText.textContent = 'Доброе утро!';
            greetingIcon.textContent = '🌤';
        } else if (hour >= 12 && hour < 18) {
            greetingText.textContent = 'Добрый день!';
            greetingIcon.textContent = '☀️';
        } else if (hour >= 18 && hour < 23) {
            greetingText.textContent = 'Добрый вечер!';
            greetingIcon.textContent = '🌆';
        } else {
            greetingText.textContent = 'Привет ночным!';
            greetingIcon.textContent = '🌙';
        }
    }

    updateGreeting();

    // Telegram WebApp
    const tg = window.Telegram?.WebApp;
    if (tg) {
        tg.ready();
        tg.expand();

        const user = tg.initDataUnsafe.user;
        if (user) {
            const avatar = document.querySelector('.user-avatar');
            if (user.photo_url) {
                avatar.src = user.photo_url;
            } else {
                avatar.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(user.first_name || 'User')}&background=4CAF50&color=fff`;
            }
        }
    }

    // Toast (простая реализация)
    window.Toast = {
        show(message) {
            const toast = document.getElementById('toast');
            toast.textContent = message;
            toast.classList.add('show');
            setTimeout(() => toast.classList.remove('show'), 3000);
        },
        info(message) { this.show(message); }
    };
});