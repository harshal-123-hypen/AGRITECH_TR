    const API_BASE = 'http://127.0.0.1:8000/api/v1';
let authToken = localStorage.getItem('authToken');

function setAuthToken(token) {
    authToken = token;
    localStorage.setItem('authToken', token);
}

function getAuthHeader() {
    if (authToken) {
        return {
            'Authorization': `Bearer ${authToken}`,
            'Content-Type': 'application/json'
        };
    }
    return { 'Content-Type': 'application/json' };
}

async function apiCall(endpoint, method = 'GET', body = null) {
    const url = `${API_BASE}${endpoint}`;
    const options = {
        method,
        headers: getAuthHeader()
    };

    if (body) {
        options.body = JSON.stringify(body);
    }

    try {
        const response = await fetch(url, options);
        if (!response.ok) {
            if (response.status === 401) {
                localStorage.removeItem('authToken');
                authToken = null;
            }
            throw new Error(`API Error: ${response.statusText}`);
        }
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

async function login(email, password) {
    try {
        const response = await fetch(`${API_BASE}/users/login?email=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        if (!response.ok) throw new Error('Login failed');

        const data = await response.json();
        setAuthToken(data.access_token);
        return data;
    } catch (error) {
        console.error('Login error:', error);
        throw error;
    }
}

async function getWeather(district) {
    return apiCall(`/weather/current/${encodeURIComponent(district)}`);
}

async function getMarketPrices(district, crop) {
    return apiCall(`/market/prices/${encodeURIComponent(district)}/${encodeURIComponent(crop)}`);
}

async function getNews() {
    return apiCall('/news/maharashtra');
}

async function getSchemes() {
    return apiCall('/schemes/popular');
}

async function detectDisease(imageBase64, crop, district) {
    return apiCall('/disease/detect-detailed', 'POST', {
        image_base64: imageBase64,
        crop,
        district
    });
}

async function predictProfit(crop, district, areaHectares) {
    return apiCall('/predictions/profit-detailed', 'POST', {
        crop,
        district,
        area_hectares: areaHectares
    });
}

async function predictRisk(crop, district) {
    return apiCall('/predictions/risk-detailed', 'POST', {
        crop,
        district
    });
}

async function getCurrentUser() {
    if (!authToken) return null;
    try {
        return await apiCall('/users/me');
    } catch {
        return null;
    }
}

function openLoginModal() {
    document.getElementById('loginModal').style.display = 'block';
}

function closeLoginModal() {
    document.getElementById('loginModal').style.display = 'none';
}

function logout() {
    localStorage.removeItem('authToken');
    authToken = null;
    location.reload();
}

function toggleAuthMode() {
    const usernameInput = document.getElementById('authUsername');
    const fullNameInput = document.getElementById('authFullName');
    
    if (usernameInput.style.display === 'none') {
        usernameInput.style.display = 'block';
        fullNameInput.style.display = 'block';
    } else {
        usernameInput.style.display = 'none';
        fullNameInput.style.display = 'none';
    }
}
