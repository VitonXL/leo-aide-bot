console.log("🔥 script.js загружается!");

document.addEventListener('DOMContentLoaded', function () {
  console.log("✅ DOM загружен");

  window.startAuth = function () {
    console.log("🎉 startAuth вызвана!");
    alert("Кнопка работает! Теперь можно делать переход.");
  };

  console.log("✅ startAuth доступна");
});
