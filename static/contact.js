
    // フォーム送信処理
document.getElementById('contact-form').addEventListener('submit', function(event) {
    event.preventDefault();

    const name = document.getElementById('field-name').value.trim();
    const email = document.getElementById('field-email').value.trim();
    const subject = document.getElementById('field-subject').value.trim();
    const message = document.getElementById('field-message').value.trim();

    const responseArea =
        document.getElementById('form-response-area');

    const payload = {
        name: name,
        email: email,
        subject: subject,
        message: message,
        lang: currentLang
    };
    fetch('/contact_send', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.message || 'メール送信に失敗しました。');
            });
        }
        return response.json();
    })
    .then(data => {
        if (data.status === 'success') {
            responseArea.innerText = data.message;
            responseArea.style.display = 'block';
            document.getElementById('contact-form').reset();
        } else {
            throw new Error(data.message || 'メール送信に失敗しました。');
        }
    })
    .catch(error => {

        console.error('Error:', error);

        responseArea.innerText = error.message;
        responseArea.style.display = 'block';
    });
});
