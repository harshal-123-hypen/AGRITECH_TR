async function initPage() {
    updateAuthUI();
    setupFileUpload();

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
        console.error('Error updating auth UI:', error);
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

function setupFileUpload() {
    const uploadArea = document.getElementById('uploadArea');
    const imageInput = document.getElementById('imageInput');

    if (!uploadArea || !imageInput) return;

    uploadArea.addEventListener('dragover', e => {
        e.preventDefault();
        uploadArea.style.borderColor = 'var(--primary-dark)';
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.style.borderColor = 'var(--primary)';
    });

    uploadArea.addEventListener('drop', e => {
        e.preventDefault();
        uploadArea.style.borderColor = 'var(--primary)';

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            imageInput.files = files;
            handleImageUpload();
        }
    });
}

function handleImageUpload() {
    const imageInput = document.getElementById('imageInput');
    const file = imageInput?.files?.[0];

    if (!file) return;

    const reader = new FileReader();
    reader.onload = e => {
        const imagePreview = document.getElementById('imagePreview');
        const previewPlaceholder = document.getElementById('previewPlaceholder');

        if (imagePreview) {
            imagePreview.src = e.target.result;
            imagePreview.style.display = 'block';
        }

        if (previewPlaceholder) {
            previewPlaceholder.style.display = 'none';
        }
    };

    reader.readAsDataURL(file);
}

function formatConfidence(confidence) {
    const value = Number(confidence);

    if (isNaN(value)) return '--';

    // जर backend 0.92 देत असेल तर 92%
    if (value <= 1) {
        return (value * 100).toFixed(1) + '%';
    }

    // जर backend 92.5 देत असेल तर 92.5%
    return value.toFixed(1) + '%';
}

function getSeverityClass(severity) {
    if (!severity) return 'severity-medium';

    const value = severity.toString().toLowerCase();

    if (value === 'severe' || value === 'high') return 'severity-high';
    if (value === 'moderate' || value === 'medium') return 'severity-medium';
    if (value === 'minor' || value === 'low' || value === 'healthy') return 'severity-low';

    return 'severity-medium';
}

function setLoadingState(isLoading) {
    const resultsLoading = document.getElementById('resultsLoading');
    const resultsContent = document.getElementById('resultsContent');

    if (resultsLoading) {
        resultsLoading.style.display = isLoading ? 'block' : 'none';
        if (isLoading) {
            resultsLoading.innerHTML = 'Analyzing image...';
        }
    }

    if (resultsContent && isLoading) {
        resultsContent.style.display = 'none';
    }
}

function renderDiseaseResult(result) {
    const diseaseResult = document.getElementById('diseaseResult');
    const confidenceResult = document.getElementById('confidenceResult');
    const severityResult = document.getElementById('severityResult');
    const treatmentResult = document.getElementById('treatmentResult');
    const recommendationsList = document.getElementById('recommendationsList');
    const resultsContent = document.getElementById('resultsContent');

    if (diseaseResult) {
        diseaseResult.textContent = result.disease || 'Unknown';
    }

    if (confidenceResult) {
        confidenceResult.textContent = formatConfidence(result.confidence);
    }

    if (severityResult) {
        severityResult.textContent = result.severity || 'Unknown';
        severityResult.className = `value ${getSeverityClass(result.severity)}`;
    }

    if (treatmentResult) {
        treatmentResult.textContent = result.treatment || 'No treatment available';
    }

    if (recommendationsList) {
        recommendationsList.innerHTML = '';

        const recommendations = Array.isArray(result.recommendations)
            ? result.recommendations
            : [];

        if (recommendations.length === 0) {
            const li = document.createElement('li');
            li.textContent = 'No recommendations available';
            recommendationsList.appendChild(li);
        } else {
            recommendations.forEach(rec => {
                const li = document.createElement('li');
                li.textContent = rec;
                recommendationsList.appendChild(li);
            });
        }
    }

    if (resultsContent) {
        resultsContent.style.display = 'block';
    }
}

async function analyzeImage() {
    const imageInput = document.getElementById('imageInput');
    const crop = document.getElementById('cropSelect').value;
    const district = document.getElementById('districtSelect').value;

    if (!imageInput || !imageInput.files.length) {
        alert('Please select an image');
        return;
    }

    if (!crop || !district) {
        alert('Please select crop and district');
        return;
    }

    const file = imageInput.files[0];
    const reader = new FileReader();

    reader.onload = async e => {
        try {
            setLoadingState(true);

            const base64Image = e.target.result.split(',')[1];

            // detectDisease function api.js मधून येते
            const result = await detectDisease(base64Image, crop, district);

            renderDiseaseResult(result);
            setLoadingState(false);
        } catch (error) {
            console.error('Disease analysis error:', error);

            setLoadingState(false);

            const resultsLoading = document.getElementById('resultsLoading');
            if (resultsLoading) {
                resultsLoading.style.display = 'block';
                resultsLoading.innerHTML = `<p style="color:red;">Failed to analyze image: ${error.message}</p>`;
            }
        }
    };

    reader.readAsDataURL(file);
}

window.addEventListener('DOMContentLoaded', initPage);