async function initPage() {
    updateAuthUI();
    setupFileUpload();
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

function setupFileUpload() {
    const uploadArea = document.getElementById('uploadArea');
    const imageInput = document.getElementById('imageInput');

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
    const file = imageInput.files[0];

    if (file) {
        const reader = new FileReader();
        reader.onload = e => {
            const imagePreview = document.getElementById('imagePreview');
            const previewPlaceholder = document.getElementById('previewPlaceholder');
            imagePreview.src = e.target.result;
            imagePreview.style.display = 'block';
            previewPlaceholder.style.display = 'none';
        };
        reader.readAsDataURL(file);
    }
}

async function analyzeImage() {
    const imageInput = document.getElementById('imageInput');
    const crop = document.getElementById('cropSelect').value;
    const district = document.getElementById('districtSelect').value;

    if (!imageInput.files.length) {
        alert('Please select an image');
        return;
    }

    if (!crop || !district) {
        alert('Please select crop and district');
        return;
    }

    const reader = new FileReader();
    reader.onload = async e => {
        const base64Image = e.target.result.split(',')[1];

        try {
            document.getElementById('resultsLoading').style.display = 'block';
            document.getElementById('resultsContent').style.display = 'none';

            const result = await detectDisease(base64Image, crop, district);

            document.getElementById('diseaseResult').textContent = result.disease;
            document.getElementById('confidenceResult').textContent = (result.confidence * 100).toFixed(1);
            document.getElementById('severityResult').textContent = result.severity;
            document.getElementById('treatmentResult').textContent = result.treatment;

            const recommendationsList = document.getElementById('recommendationsList');
            recommendationsList.innerHTML = '';
            result.recommendations.forEach(rec => {
                const li = document.createElement('li');
                li.textContent = rec;
                recommendationsList.appendChild(li);
            });

            document.getElementById('resultsLoading').style.display = 'none';
            document.getElementById('resultsContent').style.display = 'block';
        } catch (error) {
            console.error('Error:', error);
            document.getElementById('resultsLoading').innerHTML = '<p style="color:red;">Failed to analyze image</p>';
        }
    };
    reader.readAsDataURL(imageInput.files[0]);
}

window.addEventListener('DOMContentLoaded', initPage);
