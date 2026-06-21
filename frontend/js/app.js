let cropPriceChart;

async function initPage() {
    updateAuthUI();
    
    document.getElementById('authForm').addEventListener('submit', handleLogin);
    window.addEventListener('click', function(event) {
        const modal = document.getElementById('loginModal');
        if (event.target === modal) {
            closeLoginModal();
        }
    });
}

async function updateAuthUI() {
    const user = await getCurrentUser();
    const loginBtn = document.getElementById('loginBtn');
    const logoutBtn = document.getElementById('logoutBtn');
    const userDisplay = document.getElementById('userNameDisplay');

    if (user) {
        loginBtn.style.display = 'none';
        logoutBtn.style.display = 'block';
        userDisplay.textContent = `Welcome, ${user.full_name || user.username}`;
    } else {
        loginBtn.style.display = 'block';
        logoutBtn.style.display = 'none';
        userDisplay.textContent = '';
    }
}

async function handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById('authEmail').value;
    const password = document.getElementById('authPassword').value;

    try {
        await login(email, password);
        closeLoginModal();
        updateAuthUI();
        updateDashboard();
    } catch (error) {
        alert('Login failed: ' + error.message);
    }
}

async function autoDetectLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            position => {
                const { latitude, longitude } = position.coords;
                console.log(`Detected location: ${latitude}, ${longitude}`);
                alert(`Location detected: ${latitude.toFixed(4)}, ${longitude.toFixed(4)}`);
            },
            error => alert('Geolocation failed: ' + error.message)
        );
    } else {
        alert('Geolocation not supported');
    }
}

async function updateDashboard() {
    const district = document.getElementById('districtSelect').value;
    if (!district) {
        alert('Please select a district');
        return;
    }

    await loadWeather(district);
    await loadNews();
    await loadSchemes();
}

async function loadWeather(district) {
    const weatherContent = document.getElementById('weatherContent');
    const weatherLoading = document.getElementById('weatherLoading');

    try {
        weatherLoading.style.display = 'block';
        weatherContent.style.display = 'none';

        const weather = await getWeather(district);

        document.getElementById('temperature').textContent = Math.round(weather.temperature);
        document.getElementById('condition').textContent = weather.condition;
        document.getElementById('humidity').textContent = Math.round(weather.humidity) + '%';
        document.getElementById('windSpeed').textContent = weather.wind_speed.toFixed(1);
        document.getElementById('rainfall').textContent = (weather.rainfall || 0).toFixed(1);

        weatherLoading.style.display = 'none';
        weatherContent.style.display = 'block';
    } catch (error) {
        console.error('Weather error:', error);
        weatherLoading.innerHTML = '<p style="color:red;">Failed to load weather data</p>';
    }
}

async function loadNews() {
    const newsContent = document.getElementById('newsContent');
    const newsLoading = document.getElementById('newsLoading');

    try {
        newsLoading.style.display = 'block';
        newsContent.style.display = 'none';

        const data = await getNews();
        const newsList = document.getElementById('newsList');
        newsList.innerHTML = '';

        data.slice(0, 5).forEach(article => {
            const newsItem = document.createElement('div');
            newsItem.className = 'news-item';
            newsItem.innerHTML = `
                <h4>${article.title}</h4>
                <p>${article.description || 'No description'}</p>
                <p class="source">${article.source} • ${new Date(article.publish_date).toLocaleDateString()}</p>
                <a href="${article.url}" target="_blank" style="color:var(--primary);">Read More →</a>
            `;
            newsList.appendChild(newsItem);
        });

        newsLoading.style.display = 'none';
        newsContent.style.display = 'block';
    } catch (error) {
        console.error('News error:', error);
        newsLoading.innerHTML = '<p style="color:red;">Failed to load news</p>';
    }
}

async function loadSchemes() {
    const schemesContent = document.getElementById('schemesContent');
    const schemesLoading = document.getElementById('schemesLoading');

    try {
        schemesLoading.style.display = 'block';
        schemesContent.style.display = 'none';

        const data = await getSchemes();
        const schemesList = document.getElementById('schemesList');
        schemesList.innerHTML = '';

        data.schemes.slice(0, 5).forEach(scheme => {
            const schemeItem = document.createElement('div');
            schemeItem.className = 'scheme-item';
            schemeItem.innerHTML = `
                <h4>${scheme.name}</h4>
                <p>${scheme.description}</p>
                <p><strong>Ministry:</strong> ${scheme.ministry}</p>
                ${scheme.application_link ? `<a href="${scheme.application_link}" target="_blank" style="color:var(--primary);">Apply Now →</a>` : ''}
            `;
            schemesList.appendChild(schemeItem);
        });

        schemesLoading.style.display = 'none';
        schemesContent.style.display = 'block';
    } catch (error) {
        console.error('Schemes error:', error);
        schemesLoading.innerHTML = '<p style="color:red;">Failed to load schemes</p>';
    }
}

window.addEventListener('DOMContentLoaded', initPage);
