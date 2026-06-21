let profitChart;

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

    if (user) {
        loginBtn.style.display = 'none';
        logoutBtn.style.display = 'block';
    } else {
        loginBtn.style.display = 'block';
        logoutBtn.style.display = 'none';
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
    } catch (error) {
        alert('Login failed: ' + error.message);
    }
}

async function updatePredictions() {
    const crop = document.getElementById('cropSelect').value;
    const district = document.getElementById('districtSelect').value;
    const area = parseFloat(document.getElementById('areaInput').value) || 1;

    if (!crop || !district) {
        alert('Please select crop and district');
        return;
    }

    await loadProfitPrediction(crop, district, area);
    await loadRiskPrediction(crop, district);
}

async function loadProfitPrediction(crop, district, area) {
    const profitContent = document.getElementById('profitContent');
    const profitLoading = document.getElementById('profitLoading');

    try {
        profitLoading.style.display = 'block';
        profitContent.style.display = 'none';

        const prediction = await predictProfit(crop, district, area);

        document.getElementById('profitValue').textContent = `₹${prediction.predicted_profit.toFixed(0)}`;
        document.getElementById('yieldValue').textContent = `${prediction.expected_yield.toFixed(2)} qtl`;
        document.getElementById('priceValue').textContent = `₹${prediction.market_price_forecast.toFixed(0)}`;
        document.getElementById('profitConfidence').textContent = `${(prediction.confidence * 100).toFixed(1)}%`;

        profitLoading.style.display = 'none';
        profitContent.style.display = 'block';
    } catch (error) {
        console.error('Profit error:', error);
        profitLoading.innerHTML = '<p style="color:red;">Failed to load profit prediction</p>';
    }
}

async function loadRiskPrediction(crop, district) {
    const riskContent = document.getElementById('riskContent');
    const riskLoading = document.getElementById('riskLoading');

    try {
        riskLoading.style.display = 'block';
        riskContent.style.display = 'none';

        const prediction = await predictRisk(crop, district);

        const riskLevelEl = document.getElementById('riskLevel');
        riskLevelEl.textContent = prediction.risk_level.toUpperCase();
        riskLevelEl.className = `value risk-${prediction.risk_level}`;

        document.getElementById('riskScore').textContent = `${(prediction.risk_score * 100).toFixed(1)}%`;
        document.getElementById('rainfallRisk').textContent = `${(prediction.rainfall_risk * 100).toFixed(1)}%`;
        document.getElementById('pestRisk').textContent = `${(prediction.pest_risk * 100).toFixed(1)}%`;
        document.getElementById('marketRisk').textContent = `${(prediction.market_risk * 100).toFixed(1)}%`;

        const recommendationsList = document.getElementById('recommendationsList');
        recommendationsList.innerHTML = '';
        prediction.recommendations.forEach(rec => {
            const li = document.createElement('li');
            li.textContent = rec;
            recommendationsList.appendChild(li);
        });

        document.getElementById('recommendationsContent').style.display = 'block';

        riskLoading.style.display = 'none';
        riskContent.style.display = 'block';
    } catch (error) {
        console.error('Risk error:', error);
        riskLoading.innerHTML = '<p style="color:red;">Failed to load risk prediction</p>';
    }
}

window.addEventListener('DOMContentLoaded', initPage);
