document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const emailText = document.getElementById('emailText');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const loader = document.getElementById('loader');
    const resultSection = document.getElementById('resultSection');
    const classificationBadge = document.getElementById('classificationBadge');
    const classificationText = document.getElementById('classificationText');
    const responseText = document.getElementById('responseText');
    const errorAlert = document.getElementById('errorAlert');
    const errorMessage = document.getElementById('errorMessage');
    const statsCounter = document.getElementById('statsCounter');
    const charCounter = document.getElementById('charCounter');
    const clearBtn = document.getElementById('clearBtn');

    let currentFile = null;
    let analysisCount = Number(localStorage.getItem('emailAnalysisCount')) || 0;

    updateStatsDisplay();

    function validateInput() {
        analyzeBtn.disabled = !(currentFile || emailText.value.trim());
    }

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, e => {
            e.preventDefault();
            e.stopPropagation();
        }, false);
    });

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'), false);
    });

    dropZone.addEventListener('drop', e => handleFiles(e.dataTransfer.files));
    dropZone.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', () => handleFiles(fileInput.files));

    function handleFiles(files) {
        if (files.length > 0) {
            currentFile = files[0];
            emailText.value = '';
            updateFileInfo(currentFile);
            validateInput();
        }
    }

    function updateFileInfo(file) {
        const uploadText = dropZone.querySelector('.upload-text h3');
        const fileSize = (file.size / 1024).toFixed(2);
        uploadText.innerHTML = `📎 ${file.name} <span style="font-size:0.8rem;color:#6b7280">(${fileSize} KB)</span>`;
        dropZone.classList.add('file-selected');
        resultSection.style.display = 'none';
        errorAlert.style.display = 'none';
        analyzeBtn.textContent = 'Analisar e-mail';
    }

    emailText.addEventListener('input', () => {
        if (emailText.value.trim()) {
            currentFile = null;
            fileInput.value = '';
            dropZone.classList.remove('file-selected');
            const uploadText = dropZone.querySelector('.upload-text h3');
            uploadText.textContent = 'Faça upload do arquivo de e-mail';
        }
        validateInput();
        updateCharCounter();
    });

    // =========================================================================
    // ANALYZE BUTTON - CHAMADA REAL PARA API
    // =========================================================================
    analyzeBtn.addEventListener('click', async () => {
        if (!currentFile && !emailText.value.trim()) return;

        console.log('🚀 Iniciando análise...');

        analyzeBtn.disabled = true;
        loader.style.display = 'block';
        resultSection.style.display = 'none';
        errorAlert.style.display = 'none';
        analyzeBtn.textContent = 'Processando...';

        const formData = new FormData();

        if (currentFile) {
            console.log('📎 Enviando arquivo:', currentFile.name);
            formData.append('file', currentFile);
        } else {
            console.log('📝 Enviando texto:', emailText.value.length, 'caracteres');
            formData.append('email_text', emailText.value.trim());
        }

        try {
            console.log('📡 Fazendo requisição para /api/analyze...');
            
            const response = await fetch('/api/analyze', {
                method: 'POST',
                body: formData
            });

            console.log('📨 Resposta recebida - Status:', response.status);

            if (!response.ok) {
                const err = await response.json();
                console.error('❌ Erro na resposta:', err);
                throw new Error(err.detail || 'Falha na análise');
            }

            const data = await response.json();
            console.log('✅ Dados recebidos:', data);

            analysisCount++;
            localStorage.setItem('emailAnalysisCount', analysisCount);
            updateStatsDisplay();

            displayResults(data);

        } catch (error) {
            console.error('❌ Erro durante análise:', error);
            displayError(error.message);
        } finally {
            loader.style.display = 'none';
            analyzeBtn.disabled = false;
            analyzeBtn.textContent = 'Analisar outro e-mail';
        }
    });

    function displayResults(data) {
        resultSection.style.display = 'block';
        const category = (data.category || '').toLowerCase();
        let label = 'Não classificado';
        let badgeClass = 'badge-improductive';

        if (category === 'productive') {
            label = 'Produtivo';
            badgeClass = 'badge-productive';
        } else if (category === 'improductive') {
            label = 'Improdutivo';
        }

        classificationText.textContent = label;
        classificationBadge.className = `classification-badge ${badgeClass}`;
        typeWriter(data.suggested_response || '', responseText);
    }

    function displayError(msg) {
        errorAlert.style.display = 'block';
        errorMessage.textContent = msg;
    }

    function typeWriter(text, el) {
        el.textContent = '';
        let i = 0;
        (function type() {
            if (i < text.length) {
                el.textContent += text.charAt(i++);
                setTimeout(type, 15);
            }
        })();
    }

    function updateStatsDisplay() {
        statsCounter.textContent = analysisCount;
        statsCounter.classList.add('updated');
        setTimeout(() => statsCounter.classList.remove('updated'), 500);
    }

    function loadAnalysisCount() {
        return Number(localStorage.getItem('emailAnalysisCount')) || 0;
    }

    function saveAnalysisCount(count) {
        localStorage.setItem('emailAnalysisCount', count);
    }

    statsCounter.addEventListener('dblclick', () => {
        if (confirm('Deseja resetar o contador?')) {
            analysisCount = 0;
            saveAnalysisCount(0);
            updateStatsDisplay();
        }
    });

    function updateCharCounter() {
        const length = emailText.value.length;
        const maxLength = 10000;
        
        charCounter.textContent = `${length.toLocaleString('pt-BR')} / ${maxLength.toLocaleString('pt-BR')} caracteres`;
        
        charCounter.classList.remove('warning', 'limit');
        if (length > maxLength * 0.9) {
            charCounter.classList.add('limit');
        } else if (length > maxLength * 0.7) {
            charCounter.classList.add('warning');
        }
        
        clearBtn.disabled = length === 0;
    }

    clearBtn.addEventListener('click', function() {
        emailText.value = '';
        updateCharCounter();
        emailText.focus();
        emailText.dispatchEvent(new Event('input'));
    });

    updateCharCounter();
});