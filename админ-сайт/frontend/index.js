document.querySelectorAll('.btn.btn-primary').forEach(function(button) {
    button.addEventListener('click', function(event) {
        // Проверка, что нажата одна из последних четырех кнопок
        if (Array.from(document.querySelectorAll('.btn.btn-primary')).slice(-4).includes(event.target)) {
            const buttonText = event.target.textContent;
            window.location.href = '/real-estate-models?key=' + encodeURIComponent(buttonText);
        }
    });
});