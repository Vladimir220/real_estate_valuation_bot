function uploadFile() {
    document.getElementById('fileInput').click();
}

document.getElementById('fileInput').addEventListener('change', function() {
    const file = this.files[0];

    const formData = new FormData();
    formData.append('file', file);

    fetch('/upload', {
        method: 'POST',
        body: formData
    }).then(response => {
        if (response.ok) {
            document.getElementById('uploadStatus').innerText = '✅'; // Галочка
            document.querySelectorAll('.btn.btn-primary').forEach(btn => btn.disabled = false); // Активация всех кнопок
        } else {
            document.getElementById('uploadStatus').innerText = '❌'; // Крестик
        }
    }).catch(error => {
        console.error('Ошибка при загрузке файла:', error);
        document.getElementById('uploadStatus').innerText = '❌'; // Крестик
    });
});