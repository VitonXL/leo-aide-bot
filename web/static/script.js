document.addEventListener('DOMContentLoaded', () => {
    const urlInput = document.getElementById('urlInput');
    const scanBtn = document.getElementById('scanBtn');
    const resultDiv = document.getElementById('result');
    const loader = document.getElementById('loader');
    const report = document.getElementById('report');

    // Тема
    const urlParams = new URLSearchParams(window.location.search);
    const theme = urlParams.get('theme');
    if (theme === 'dark') {
        document.body.classList.add('dark');
    }

    scanBtn.addEventListener('click', async () => {
        const url = urlInput.value.trim();
        if (!url) {
            alert('Введите URL');
            return;
        }

        resultDiv.classList.remove('hidden');
        loader.style.display = 'block';
        report.innerHTML = '';

        try {
            const response = await fetch('/scan', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url })
            });

            const data = await response.json();

            if (data.success) {
                checkResult(data.scan_id);
            } else {
                report.innerHTML = `<p style="color: red">❌ Ошибка: ${data.error}</p>`;
                loader.style.display = 'none';
            }
        } catch (err) {
            report.innerHTML = `<p style="color: red">❌ Ошибка сети</p>`;
            loader.style.display = 'none';
        }
    });

    function checkResult(scan_id) {
        const interval = setInterval(async () => {
            const res = await fetch(`/result/${scan_id}`);
            const data = await res.json();

            if (data.status === 'completed') {
                clearInterval(interval);
                loader.style.display = 'none';

                const total = Object.values(data.stats).reduce((a, b) => a + b, 0);
                const malicious = data.stats.malicious || 0;

                if (malicious > 0) {
                    report.innerHTML = `
                        <p>🔴 <b>Опасно!</b></p>
                        <p>Обнаружено угроз: <b style="color: red">${malicious}</b></p>
                    `;
                } else {
                    report.innerHTML = `
                        <p>🟢 <b>Безопасно</b></p>
                        <p>Проверено: ${total} антивирусов</p>
                    `;
                }
            }
        }, 3000);
    }
});
