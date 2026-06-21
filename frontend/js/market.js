let priceChart;

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

async function updateMarketPrices() {
    const district = document.getElementById('districtSelect').value;
    const crop = document.getElementById('cropSelect').value;

    if (!district || !crop) {
        alert('Please select both district and crop');
        return;
    }

    await loadPrices(district, crop);
}

async function loadPrices(district, crop) {
    const pricesLoading = document.getElementById('pricesLoading');
    const pricesContent = document.getElementById('pricesContent');
    const tableBody = document.getElementById('pricesTableBody');

    try {
        pricesLoading.style.display = 'block';
        pricesContent.style.display = 'none';

        const prices = await getMarketPrices(district, crop);

        tableBody.innerHTML = '';
        prices.forEach(price => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${price.market_name}</td>
                <td>${price.crop}</td>
                <td>₹${price.today_price.toFixed(2)}</td>
                <td>₹${price.min_price.toFixed(2)}</td>
                <td>₹${price.max_price.toFixed(2)}</td>
                <td>₹${price.modal_price.toFixed(2)}</td>
                <td>${new Date(price.last_updated).toLocaleDateString()}</td>
            `;
            tableBody.appendChild(row);
        });

        pricesLoading.style.display = 'none';
        pricesContent.style.display = 'block';
    } catch (error) {
        console.error('Error:', error);
        pricesLoading.innerHTML = '<p style="color:red;">Failed to load market prices</p>';
    }
}

async function refreshPrices() {
    await updateMarketPrices();
}

window.addEventListener('DOMContentLoaded', initPage);
