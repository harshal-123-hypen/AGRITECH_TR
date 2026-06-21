var FarmerAssistant = window.FarmerAssistant || (() => {
    const langMap = {
        en: { code: 'en-IN', names: ['English', 'India'] },
        hi: { code: 'hi-IN', names: ['Hindi', 'हिन्दी', 'हिंदी', 'Heera', 'Kalpana'] },
        mr: { code: 'mr-IN', names: ['Marathi', 'मराठी', 'Aarohi', 'Manohar'] }
    };

    const defaultMessages = {
        en: 'Welcome to Maharashtra Agriculture. You can say weather, market price, prediction, disease, scheme, or equipment.',
        hi: 'महाराष्ट्र कृषि पोर्टल में आपका स्वागत है। आप मौसम, बाजार भाव, भविष्यवाणी, रोग, योजना या उपकरण बोल सकते हैं।',
        mr: 'महाराष्ट्र कृषी पोर्टलमध्ये आपले स्वागत आहे. तुम्ही हवामान, बाजारभाव, अंदाज, रोग, योजना किंवा उपकरण असे बोलू शकता.'
    };

    let voices = [];

    function refreshVoices() {
        if ('speechSynthesis' in window) {
            voices = window.speechSynthesis.getVoices();
        }
    }

    if ('speechSynthesis' in window) {
        refreshVoices();
        window.speechSynthesis.onvoiceschanged = refreshVoices;
    }

    function getLanguage() {
        const select = document.getElementById('languageSelect');
        const value = select ? select.value : localStorage.getItem('farmerAssistantLang');
        return langMap[value] ? value : 'en';
    }

    function setLanguage(lang) {
        if (langMap[lang]) localStorage.setItem('farmerAssistantLang', lang);
    }

    function chooseVoice(lang) {
        refreshVoices();
        const target = langMap[lang] || langMap.en;
        const byLang = voices.find(v => v.lang && v.lang.toLowerCase() === target.code.toLowerCase());
        if (byLang) return byLang;

        const byPrefix = voices.find(v => v.lang && v.lang.toLowerCase().startsWith(target.code.slice(0, 2).toLowerCase()));
        if (byPrefix) return byPrefix;

        const byName = voices.find(v => target.names.some(name => v.name.toLowerCase().includes(name.toLowerCase())));
        if (byName) return byName;

        if (lang === 'mr') {
            return chooseVoice('hi') || chooseVoice('en');
        }
        return voices.find(v => v.lang && v.lang.toLowerCase().startsWith('en')) || voices[0] || null;
    }

    function speak(text, lang = getLanguage()) {
        if (!('speechSynthesis' in window)) {
            alert('Voice assistant is not supported in this browser.');
            return;
        }

        const finalText = text || defaultMessages[lang] || defaultMessages.en;
        window.speechSynthesis.cancel();

        const utterance = new SpeechSynthesisUtterance(finalText);
        utterance.lang = (langMap[lang] || langMap.en).code;
        utterance.rate = lang === 'en' ? 0.92 : 0.84;
        utterance.pitch = 1;

        const voice = chooseVoice(lang);
        if (voice) utterance.voice = voice;

        window.speechSynthesis.speak(utterance);
    }

    function stop() {
        if ('speechSynthesis' in window) window.speechSynthesis.cancel();
    }

    function getRecognizer() {
        return window.SpeechRecognition || window.webkitSpeechRecognition || null;
    }

    function startListening(callback) {
        const Recognition = getRecognizer();
        const status = document.getElementById('assistantCommandResult');

        if (!Recognition) {
            const msg = 'Speech input is not supported in this browser. Please use Chrome or Edge.';
            if (status) status.textContent = msg;
            alert(msg);
            return;
        }

        const lang = getLanguage();
        const recognition = new Recognition();
        recognition.lang = (langMap[lang] || langMap.en).code;
        recognition.interimResults = false;
        recognition.continuous = false;

        if (status) status.textContent = lang === 'mr' ? 'ऐकत आहे... बोला.' : lang === 'hi' ? 'सुन रहा हूँ... बोलिए।' : 'Listening... speak now.';

        recognition.onresult = event => {
            const transcript = event.results[0][0].transcript;
            if (status) status.textContent = transcript;
            if (callback) callback(transcript);
            else handleCommand(transcript);
        };

        recognition.onerror = event => {
            const msg = `Voice input error: ${event.error}`;
            if (status) status.textContent = msg;
        };

        recognition.start();
    }

    function saveHistory(type, details) {
        const history = JSON.parse(localStorage.getItem('farmerHistory') || '[]');
        history.unshift({
            type,
            details,
            time: new Date().toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' })
        });
        localStorage.setItem('farmerHistory', JSON.stringify(history.slice(0, 30)));
        renderHistory();
    }

    function getHistory() {
        return JSON.parse(localStorage.getItem('farmerHistory') || '[]');
    }

    function renderHistory() {
        const list = document.getElementById('farmerHistoryList');
        if (!list) return;

        const history = getHistory();
        if (!history.length) {
            list.innerHTML = '<div class="history-empty">No farmer activity saved yet.</div>';
            return;
        }

        list.innerHTML = history.map(item => `
            <div class="history-item">
                <strong>${getHistoryIcon(item.type)} ${item.type}</strong>
                <span>${item.details}</span>
                <small>${item.time}</small>
            </div>
        `).join('');
    }

    function getHistoryIcon(type) {
        const value = String(type || '').toLowerCase();
        if (value.includes('weather')) return '🌦️';
        if (value.includes('market')) return '📈';
        if (value.includes('prediction')) return '📊';
        if (value.includes('equipment')) return '🛠️';
        if (value.includes('voice')) return '🎙️';
        if (value.includes('disease')) return '🌱';
        return '📌';
    }

    function clearHistory() {
        localStorage.removeItem('farmerHistory');
        renderHistory();
    }

    function includesAny(text, words) {
        const value = text.toLowerCase();
        return words.some(word => value.includes(word.toLowerCase()));
    }

    function scrollToTarget(selector) {
        const el = document.querySelector(selector);
        if (el) {
            el.scrollIntoView({ behavior: 'smooth', block: 'start' });
            return true;
        }
        return false;
    }

    function handleCommand(transcript) {
        const text = transcript || '';
        const lang = getLanguage();
        const status = document.getElementById('assistantCommandResult');

        let action = '';
        if (includesAny(text, ['weather', 'havaman', 'हवामान', 'मौसम', 'rain', 'पाऊस', 'बारिश'])) {
            if (!scrollToTarget('#weather-section')) setTimeout(() => { window.location.href = 'index.html#weather-section'; }, 700);
            action = lang === 'mr' ? 'हवामान अहवाल दाखवत आहे.' : lang === 'hi' ? 'मौसम रिपोर्ट दिखा रहा हूँ।' : 'Showing weather report.';
        } else if (includesAny(text, ['market', 'mandi', 'price', 'बाजार', 'भाव', 'मंडी', 'किंमत'])) {
            if (!scrollToTarget('#market-section')) setTimeout(() => { window.location.href = 'index.html#market-section'; }, 700);
            action = lang === 'mr' ? 'बाजारभाव दाखवत आहे.' : lang === 'hi' ? 'बाजार भाव दिखा रहा हूँ।' : 'Showing market prices.';
        } else if (includesAny(text, ['scheme', 'yojana', 'योजना', 'subsidy', 'अनुदान'])) {
            if (!scrollToTarget('#schemes-section')) setTimeout(() => { window.location.href = 'index.html#schemes-section'; }, 700);
            action = lang === 'mr' ? 'सरकारी योजना दाखवत आहे.' : lang === 'hi' ? 'सरकारी योजनाएं दिखा रहा हूँ।' : 'Showing government schemes.';
        } else if (includesAny(text, ['disease', 'rog', 'रोग', 'बीमारी', 'leaf', 'पान'])) {
            action = lang === 'mr' ? 'रोग ओळख पान उघडत आहे.' : lang === 'hi' ? 'रोग पहचान पेज खोल रहा हूँ।' : 'Opening disease detection.';
            setTimeout(() => { window.location.href = 'disease.html'; }, 700);
        } else if (includesAny(text, ['prediction', 'predict', 'profit', 'risk', 'अंदाज', 'भविष्यवाणी', 'लाभ', 'नफा', 'जोखीम'])) {
            action = lang === 'mr' ? 'पीक अंदाज पान उघडत आहे.' : lang === 'hi' ? 'भविष्यवाणी पेज खोल रहा हूँ।' : 'Opening predictions.';
            setTimeout(() => { window.location.href = 'predictions.html'; }, 700);
        } else if (includesAny(text, ['equipment', 'tool', 'machine', 'उपकरण', 'औजार', 'मशीन', 'साधन'])) {
            action = lang === 'mr' ? 'उपकरण शोध पान उघडत आहे.' : lang === 'hi' ? 'उपकरण खोज पेज खोल रहा हूँ।' : 'Opening equipment finder.';
            setTimeout(() => { window.location.href = 'equipment.html'; }, 700);
        } else {
            action = lang === 'mr'
                ? 'मला समजले नाही. हवामान, बाजारभाव, अंदाज, रोग, योजना किंवा उपकरण बोला.'
                : lang === 'hi'
                    ? 'मैं समझ नहीं पाया। मौसम, बाजार भाव, भविष्यवाणी, रोग, योजना या उपकरण बोलिए।'
                    : 'I did not understand. Say weather, market price, prediction, disease, scheme, or equipment.';
        }

        if (status) status.textContent = action;
        saveHistory('Voice command', text);
        speak(action, lang);
    }

    function init() {
        const select = document.getElementById('languageSelect');
        if (select) {
            const saved = localStorage.getItem('farmerAssistantLang');
            if (saved && langMap[saved]) select.value = saved;
            select.addEventListener('change', () => {
                setLanguage(select.value);
                if (typeof window.changeLanguage === 'function') window.changeLanguage(select.value);
                if (typeof window.changePageLanguage === 'function') window.changePageLanguage(select.value);
            });
            const activeLang = select.value;
            if (typeof window.changeLanguage === 'function') window.changeLanguage(activeLang);
            if (typeof window.changePageLanguage === 'function') window.changePageLanguage(activeLang);
        }
        renderHistory();
    }

    window.addEventListener('DOMContentLoaded', init);

    return {
        speak,
        stop,
        startListening,
        handleCommand,
        saveHistory,
        getHistory,
        renderHistory,
        clearHistory,
        getLanguage
    };
})();

window.FarmerAssistant = FarmerAssistant;
