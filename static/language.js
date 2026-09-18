let currentLang = 'en';

function setLanguage(lang) {

    fetch('/switch_language', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            lang: lang
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Language switch failed');
        }

        return response.json();
    })
    .then(result => {

        if (result.status !== 'success') {
            throw new Error(result.message || 'Language switch failed');
        }

        const data = result.data;
        window.currentContactData = data;
        
        document.getElementById('contact-text-p').innerText = data.intro;
        document.getElementById('contact-heading').innerText = data.heading;
        document.getElementById('contact-subheading').innerText = data.subheading;
        document.getElementById('achievements-title').innerText = data.achTitle;
        document.getElementById('achievements-content').innerText = data.achContent;

        document.getElementById('field-name').placeholder =
            data.placeholders.name;
        document.getElementById('field-email').placeholder =
            data.placeholders.email;

        document.getElementById('field-subject').placeholder =
            data.placeholders.subject;

        document.getElementById('field-message').placeholder =
            data.placeholders.message;

        document.getElementById('btn-send').innerText =
            data.sendBtn;

        const jaElements = document.querySelectorAll('.lang-ja');
        const enElements = document.querySelectorAll('.lang-en');

        if (lang === 'ja') {
            jaElements.forEach(el => {
                el.style.display = 'inline';
            });

            enElements.forEach(el => {
                el.style.display = 'none';
            });
        } else {
            jaElements.forEach(el => {
                el.style.display = 'none';
            });

            enElements.forEach(el => {
                el.style.display = 'inline';
            });
        }
        const btnJa = document.getElementById('lang-btn-ja');
        const btnEn = document.getElementById('lang-btn-en');

        if (lang === 'ja') {

            if (btnJa) btnJa.classList.add('active');
            if (btnEn) btnEn.classList.remove('active');

        } else {

            if (btnEn) btnEn.classList.add('active');
            if (btnJa) btnJa.classList.remove('active');
        }


        currentLang = lang;

        localStorage.setItem('selectedLang', lang);
    })
    .catch(error => {
        console.error('Language switch error:', error);
    });
}

document.addEventListener("DOMContentLoaded", function() {
    const savedLang = localStorage.getItem('selectedLang') || 'en';

    setLanguage(savedLang);
});
