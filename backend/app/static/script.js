document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const loader = document.getElementById('loader');
    const resultSection = document.getElementById('resultSection');
    const classificationBadge = document.getElementById('classificationBadge');
    const classificationText = document.getElementById('classificationText');
    const responseText = document.getElementById('responseText');
    const errorAlert = document.getElementById('errorAlert');
    const errorMessage = document.getElementById('errorMessage');
    const statsCounter = document.getElementById('statsCounter');

    let currentFile = null;
    let analysisCount = loadAnalysisCount();

    updateStatsDisplay();

    // =========================================================================
    // DRAG & DROP EVENTS
    // =========================================================================
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });

    function highlight() {
        dropZone.classList.add('dragover');
    }

    function unhighlight() {
        dropZone.classList.remove('dragover');
    }

    dropZone.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        handleFiles(e.dataTransfer.files);
    }

    dropZone.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', function () {
        handleFiles(this.files);
    });

    function handleFiles(files) {
        if (files.length > 0) {
            currentFile = files[0];
            updateFileInfo(currentFile);
        }
    }

    function updateFileInfo(file) {
        const uploadText = dropZone.querySelector('.upload-text h3');
        const fileSize = (file.size / 1024).toFixed(2);
        uploadText.innerHTML = `📎 ${file.name} <span style="font-size: 0.8rem; color: #6b7280;">(${fileSize} KB)</span>`;
        analyzeBtn.disabled = false;
        resultSection.style.display = 'none';
        errorAlert.style.display = 'none';
        analyzeBtn.textContent = 'Analisar e-mail';
    }

    // =========================================================================
    // ANALYZE BUTTON CLICK
    // =========================================================================
    analyzeBtn.addEventListener('click', async () => {
        if (!currentFile) return;

        analyzeBtn.disabled = true;
        loader.style.display = 'block';
        resultSection.style.display = 'none';
        errorAlert.style.display = 'none';
        analyzeBtn.textContent = 'Processando...';

        const formData = new FormData();
        formData.append('file', currentFile);

        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Falha na análise');
            }

            const data = await response.json();

            analysisCount++;
            saveAnalysisCount(analysisCount);
            updateStatsDisplay();

            displayResults(data);

        } catch (error) {
            displayError(error.message);
        } finally {
            loader.style.display = 'none';
            analyzeBtn.disabled = false;
            analyzeBtn.textContent = 'Analisar outro arquivo';
        }
    });

    // =========================================================================
    // DISPLAY RESULTS (CORRIGIDO)
    // =========================================================================
    function displayResults(data) {
        resultSection.style.display = 'block';

        const rawCategory = (data.category || '').toLowerCase();

        let label = 'Não classificado';
        let badgeClass = 'badge-improductive';

        if (rawCategory === 'productive') {
            label = 'Produtivo';
            badgeClass = 'badge-productive';
        } else if (rawCategory === 'improductive') {
            label = 'Improdutivo';
            badgeClass = 'badge-improductive';
        }

        classificationText.textContent = label;
        classificationBadge.className = `classification-badge ${badgeClass}`;

        typeWriter(data.suggested_response || '', responseText);
    }

    // =========================================================================
    // DISPLAY ERROR
    // =========================================================================
    function displayError(errorMsg) {
        errorAlert.style.display = 'block';

        let friendlyMessage = errorMsg;
        let icon = '⚠️';
        let suggestions = [];

        if (errorMsg.includes('empty') || errorMsg.includes('vazio')) {
            icon = '📄';
            friendlyMessage = 'O arquivo parece estar vazio ou não contém texto legível.';
            suggestions = [
                'Verifique se o PDF não está protegido',
                'Tente outro formato',
                'Use um arquivo .txt'
            ];
        } else if (errorMsg.includes('format') || errorMsg.includes('formato')) {
            icon = '❌';
            friendlyMessage = 'Formato de arquivo não suportado.';
        } else if (errorMsg.includes('size') || errorMsg.includes('tamanho')) {
            icon = '📦';
            friendlyMessage = 'O arquivo é muito grande.';
        } else if (errorMsg.includes('network') || errorMsg.includes('fetch')) {
            icon = '🌐';
            friendlyMessage = 'Erro de conexão com o servidor.';
        }

        errorMessage.innerHTML = `
            <div style="display:flex;gap:1rem;">
                <div style="font-size:2rem">${icon}</div>
                <div>
                    <h4 style="color:#dc2626">Oops! Algo deu errado</h4>
                    <p>${friendlyMessage}</p>
                    ${suggestions.length ? `
                        <ul>${suggestions.map(s => `<li>${s}</li>`).join('')}</ul>
                    ` : ''}
                </div>
            </div>
        `;
    }

    // =========================================================================
    // TYPING EFFECT
    // =========================================================================
    function typeWriter(text, element) {
        element.textContent = '';
        let i = 0;

        function type() {
            if (i < text.length) {
                element.textContent += text.charAt(i++);
                setTimeout(type, 15);
            }
        }
        type();
    }

    // =========================================================================
    // STATISTICS
    // =========================================================================
    function loadAnalysisCount() {
        return parseInt(localStorage.getItem('emailAnalysisCount')) || 0;
    }

    function saveAnalysisCount(count) {
        localStorage.setItem('emailAnalysisCount', count);
        localStorage.setItem('lastAnalysisDate', new Date().toISOString());
    }

    function updateStatsDisplay() {
        if (statsCounter) {
            statsCounter.textContent = analysisCount;
            statsCounter.style.transform = 'scale(1.2)';
            setTimeout(() => statsCounter.style.transform = 'scale(1)', 200);
        }
    }

    function resetStats() {
        if (confirm('Deseja resetar o contador de análises?')) {
            analysisCount = 0;
            saveAnalysisCount(0);
            updateStatsDisplay();
        }
    }

    window.resetEmailStats = resetStats;

    if (statsCounter) {
        statsCounter.addEventListener('dblclick', resetStats);
    }
});
