let profitChart;

async function initPage() {
    updateAuthUI();

    const authForm = document.getElementById('authForm');
    if (authForm) {
        authForm.addEventListener('submit', handleLogin);
    }

    window.addEventListener('click', function (event) {
        const modal = document.getElementById('loginModal');
        if (modal && event.target === modal) {
            closeLoginModal();
        }
    });
}

async function updateAuthUI() {
    try {
        const user = await getCurrentUser();
        const loginBtn = document.getElementById('loginBtn');
        const logoutBtn = document.getElementById('logoutBtn');

        if (!loginBtn || !logoutBtn) return;

        if (user) {
            loginBtn.style.display = 'none';
            logoutBtn.style.display = 'block';
        } else {
            loginBtn.style.display = 'block';
            logoutBtn.style.display = 'none';
        }
    } catch (error) {
        console.error('Auth UI update failed:', error);
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
        alert('Login successful');
    } catch (error) {
        alert('Login failed: ' + error.message);
    }
}

async function updatePredictions() {
    const crop = document.getElementById('cropSelect').value;
    const district = document.getElementById('districtSelect').value;
    const area = parseFloat(document.getElementById('areaInput').value) || 1;

    // Temporary input fields नसतील तर default values
    const rainfall = parseFloat(document.getElementById('rainfallInput')?.value) || 800;
    const temperature = parseFloat(document.getElementById('temperatureInput')?.value) || 28;
    const marketPrice = parseFloat(document.getElementById('marketPriceInput')?.value) || 2500;

    if (!crop || !district) {
        alert('Please select crop and district');
        return;
    }

    await loadProfitPrediction(crop, district, rainfall, temperature, area, marketPrice);
    await loadRiskPrediction(crop, district);
}

async function loadProfitPrediction(crop, district, rainfall, temperature, area, marketPrice) {
    const profitContent = document.getElementById('profitContent');
    const profitLoading = document.getElementById('profitLoading');

    try {
        if (profitLoading) {
            profitLoading.style.display = 'block';
            profitLoading.innerHTML = 'Loading profit prediction...';
        }

        if (profitContent) {
            profitContent.style.display = 'none';
        }

        // api.js मधली updated function
        const prediction = await predictProfit(
            crop,
            district,
            rainfall,
            temperature,
            area,
            marketPrice
        );

        // Backend currently returns only: { profit: number }
        const profit = Number(prediction.profit || 0);

        const profitValue = document.getElementById('profitValue');
        const yieldValue = document.getElementById('yieldValue');
        const priceValue = document.getElementById('priceValue');
        const profitConfidence = document.getElementById('profitConfidence');

        if (profitValue) {
            profitValue.textContent = `₹${profit.toFixed(0)}`;
        }

        // Temporary derived/demo values until backend gives real values
        if (yieldValue) {
            yieldValue.textContent = `${(area * 18).toFixed(2)} qtl`;
        }

        if (priceValue) {
            priceValue.textContent = `₹${Number(marketPrice).toFixed(0)}`;
        }

        if (profitConfidence) {
            profitConfidence.textContent = `85.0%`;
        }

        if (profitLoading) {
            profitLoading.style.display = 'none';
        }

        if (profitContent) {
            profitContent.style.display = 'block';
        }

    } catch (error) {
        console.error('Profit prediction error:', error);

        if (profitLoading) {
            profitLoading.style.display = 'block';
            profitLoading.innerHTML = `<p style="color:red;">Failed to load profit prediction: ${error.message}</p>`;
        }
    }
}

async function loadRiskPrediction(crop, district) {
    const riskContent = document.getElementById('riskContent');
    const riskLoading = document.getElementById('riskLoading');
    const recommendationsContent = document.getElementById('recommendationsContent');

    try {
        if (riskLoading) {
            riskLoading.style.display = 'block';
            riskLoading.innerHTML = 'Loading risk prediction...';
        }

        if (riskContent) {
            riskContent.style.display = 'none';
        }

        // Current backend मध्ये risk API नाही
        // म्हणून temporary demo data वापरतो
        const prediction = {
            risk_level: 'medium',
            risk_score: 0.42,
            rainfall_risk: 0.35,
            pest_risk: 0.48,
            market_risk: 0.43,
            recommendations: [
                'Monitor rainfall and irrigation schedule carefully.',
                'Use preventive pest control measures.',
                'Track mandi prices before harvest.',
                'Maintain balanced fertilizer usage.',
                'Review crop health weekly.'
            ]
        };

        const riskLevelEl = document.getElementById('riskLevel');
        if (riskLevelEl) {
            riskLevelEl.textContent = prediction.risk_level.toUpperCase();
            riskLevelEl.className = `value risk-${prediction.risk_level}`;
        }

        const riskScore = document.getElementById('riskScore');
        const rainfallRisk = document.getElementById('rainfallRisk');
        const pestRisk = document.getElementById('pestRisk');
        const marketRisk = document.getElementById('marketRisk');

        if (riskScore) {
            riskScore.textContent = `${(prediction.risk_score * 100).toFixed(1)}%`;
        }

        if (rainfallRisk) {
            rainfallRisk.textContent = `${(prediction.rainfall_risk * 100).toFixed(1)}%`;
        }

        if (pestRisk) {
            pestRisk.textContent = `${(prediction.pest_risk * 100).toFixed(1)}%`;
        }

        if (marketRisk) {
            marketRisk.textContent = `${(prediction.market_risk * 100).toFixed(1)}%`;
        }

        const recommendationsList = document.getElementById('recommendationsList');
        if (recommendationsList) {
            recommendationsList.innerHTML = '';

            prediction.recommendations.forEach(rec => {
                const li = document.createElement('li');
                li.textContent = rec;
                recommendationsList.appendChild(li);
            });
        }

        if (recommendationsContent) {
            recommendationsContent.style.display = 'block';
        }

        if (riskLoading) {
            riskLoading.style.display = 'none';
        }

        if (riskContent) {
            riskContent.style.display = 'block';
        }

    } catch (error) {
        console.error('Risk prediction error:', error);

        if (riskLoading) {
            riskLoading.style.display = 'block';
            riskLoading.innerHTML = `<p style="color:red;">Failed to load risk prediction: ${error.message}</p>`;
        }
    }
}

window.addEventListener('DOMContentLoaded', initPage);