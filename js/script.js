const textarea = document.getElementById('folderPaths');
const statusDiv = document.getElementById('status');
const btn = document.getElementById('generateBtn');
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const treePreview = document.getElementById('treePreview');

// Structural Preset Constants
const templates = {
    web: "src/components\nsrc/hooks\nsrc/assets/images\nsrc/assets/styles\npublic/locales\nconfig\ntests",
    data: "data/raw\ndata/processed\nnotebooks\nsrc/models\nsrc/features\nreferences\nreports/figures",
    python: "src/module_name\ntests\ndocs\nexamples\nconfig\nscripts"
};

function loadPreset(key) {
    textarea.value = templates[key];
    updateTreePreview();
    clearStatus();
}

function clearWorkspace() {
    textarea.value = "";
    updateTreePreview();
    clearStatus();
}

function clearStatus() {
    statusDiv.style.display = 'none';
}

// Process Text Input to Object Tree Layout Logic
function updateTreePreview() {
    const text = textarea.value.trim();
    if (!text) {
        treePreview.innerHTML = '<span style="color: #64748b; font-style: italic;">Your live folder blueprint will appear here...</span>';
        return;
    }

    const lines = text.split('\n');
    const treeData = {};

    lines.forEach(line => {
        const clean = line.trim();
        if (clean) {
            const segments = clean.split('/').filter(s => s.trim() !== '');
            let currentLevel = treeData;
            segments.forEach(segment => {
                if (!currentLevel[segment]) {
                    currentLevel[segment] = {};
                }
                currentLevel = currentLevel[segment];
            });
        }
    });

    if (Object.keys(treeData).length === 0) {
        treePreview.innerHTML = '<span style="color: #64748b; font-style: italic;">Your live folder blueprint will appear here...</span>';
        return;
    }

    treePreview.innerHTML = "";
    treePreview.appendChild(renderHTMLTree(treeData));
}

function renderHTMLTree(obj) {
    const ul = document.createElement('ul');
    for (const key in obj) {
        const li = document.createElement('li');
        li.innerHTML = `📁 <span style="color: #f1f5f9;">${key}</span>`;
        if (Object.keys(obj[key]).length > 0) {
            li.appendChild(renderHTMLTree(obj[key]));
        }
        ul.appendChild(li);
    }
    return ul;
}

// Monitor Text Input for Live Rendering
textarea.addEventListener('input', updateTreePreview);

// File Upload Reading Utility
function handleFile(file) {
    if (!file || file.type !== "text/plain" && !file.name.endsWith('.txt')) {
        showStatus("Invalid file format. Please upload a pure plain text (.txt) file layout.", "error");
        return;
    }
    
    const reader = new FileReader();
    reader.onload = function(e) {
        textarea.value = e.target.result;
        updateTreePreview();
        showStatus(`Loaded layout configuration from "${file.name}" successfully!`, "success");
    };
    reader.readAsText(file);
}

fileInput.addEventListener('change', (e) => handleFile(e.target.files[0]));

// Drag and Drop Events
['dragenter', 'dragover'].forEach(eventName => {
    dropZone.addEventListener(eventName, (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    }, false);
});

['dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
    }, false);
});

dropZone.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    const files = dt.files;
    handleFile(files[0]);
});

// Generate Pipeline Action Execution
btn.addEventListener('click', async () => {
    const text = textarea.value.trim();
    
    const showStatusMsg = (msg, type) => {
        statusDiv.style.display = 'block';
        statusDiv.textContent = msg;
        if (type === 'error') {
            statusDiv.style.backgroundColor = '#fef2f2';
            statusDiv.style.color = '#ef4444';
            statusDiv.style.border = '1px solid #fee2e2';
        } else if (type === 'success') {
            statusDiv.style.backgroundColor = '#f0fdf4';
            statusDiv.style.color = '#16a34a';
            statusDiv.style.border = '1px solid #dcfce7';
        } else {
            statusDiv.style.backgroundColor = '#f8fafc';
            statusDiv.style.color = '#64748b';
            statusDiv.style.border = '1px solid #e2e8f0';
        }
    };

    if (!text) {
        showStatusMsg('Please enter or import at least one folder pathway structural configuration rule.', 'error');
        return;
    }

    btn.disabled = true;
    showStatusMsg('Compiling zip compression target runtime structure arrays...', 'info');

    try {
        const zip = new JSZip();
        const lines = text.split('\n');
        let folderCount = 0;

        lines.forEach(line => {
            const cleanedPath = line.trim();
            if (cleanedPath) {
                zip.folder(cleanedPath);
                folderCount++;
            }
        });

        if (folderCount === 0) throw new Error('No valid nested data pathways declared.');

        const content = await zip.generateAsync({ type: 'blob' });
        const url = window.URL.createObjectURL(content);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'generated_folders.zip';
        
        document.body.appendChild(a);
        a.click();
        
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        showStatusMsg(`Successfully packaged ${folderCount} directories! Your ZIP download has started.`, 'success');
    } catch (error) {
        showStatusMsg(`Execution error exception halted download: ${error.message}`, 'error');
    } finally {
        btn.disabled = false;
    }
});

function showStatus(msg, type) {
    statusDiv.style.display = 'block';
    statusDiv.textContent = msg;
    if (type === 'error') {
        statusDiv.style.backgroundColor = '#fef2f2';
        statusDiv.style.color = '#ef4444';
        statusDiv.style.border = '1px solid #fee2e2';
    } else if (type === 'success') {
        statusDiv.style.backgroundColor = '#f0fdf4';
        statusDiv.style.color = '#16a34a';
        statusDiv.style.border = '1px solid #dcfce7';
    }
}