// State management
let authToken = localStorage.getItem('authToken');
let userEmail = localStorage.getItem('userEmail');

// API base URL
const API_BASE = '';

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    if (authToken) {
        verifyTokenAndShowDashboard();
    } else {
        showAuthContainer();
    }

    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    // Auth form switching
    document.getElementById('show-register').addEventListener('click', (e) => {
        e.preventDefault();
        document.getElementById('login-form').style.display = 'none';
        document.getElementById('register-form').style.display = 'block';
        hideError();
    });

    document.getElementById('show-login').addEventListener('click', (e) => {
        e.preventDefault();
        document.getElementById('register-form').style.display = 'none';
        document.getElementById('login-form').style.display = 'block';
        hideError();
    });

    // Login form
    document.getElementById('login-form').addEventListener('submit', handleLogin);

    // Register form
    document.getElementById('register-form').addEventListener('submit', handleRegister);

    // Logout button
    document.getElementById('logout-btn').addEventListener('click', handleLogout);

    // File upload
    const uploadArea = document.getElementById('upload-area');
    const fileInput = document.getElementById('file-input');

    uploadArea.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFileSelect);

    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('drag-over');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('drag-over');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('drag-over');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileUpload(files[0]);
        }
    });

    // Query form
    document.getElementById('query-form').addEventListener('submit', handleQuery);
}

// Authentication functions
async function handleRegister(e) {
    e.preventDefault();

    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;
    const confirmPassword = document.getElementById('register-password-confirm').value;

    if (password !== confirmPassword) {
        showError('Passwords do not match');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Registration failed');
        }

        // Auto login after registration
        await handleLoginRequest(email, password);
    } catch (error) {
        showError(error.message);
    }
}

async function handleLogin(e) {
    e.preventDefault();

    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;

    await handleLoginRequest(email, password);
}

async function handleLoginRequest(email, password) {
    try {
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Login failed');
        }

        const data = await response.json();
        authToken = data.access_token;
        userEmail = email;

        localStorage.setItem('authToken', authToken);
        localStorage.setItem('userEmail', userEmail);

        showDashboard();
    } catch (error) {
        showError(error.message);
    }
}

async function verifyTokenAndShowDashboard() {
    try {
        const response = await fetch(`${API_BASE}/auth/me`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        if (!response.ok) {
            throw new Error('Token invalid');
        }

        const user = await response.json();
        userEmail = user.email;
        localStorage.setItem('userEmail', userEmail);

        showDashboard();
    } catch (error) {
        // Token invalid, show login
        handleLogout();
    }
}

function handleLogout() {
    authToken = null;
    userEmail = null;
    localStorage.removeItem('authToken');
    localStorage.removeItem('userEmail');
    showAuthContainer();
    clearDashboard();
}

// UI functions
function showAuthContainer() {
    document.getElementById('auth-container').style.display = 'flex';
    document.getElementById('dashboard-container').style.display = 'none';
}

function showDashboard() {
    document.getElementById('auth-container').style.display = 'none';
    document.getElementById('dashboard-container').style.display = 'flex';
    document.getElementById('user-email').textContent = userEmail;
    hideError();

    // Load user's documents and history
    loadDocuments();
}

function showError(message) {
    const errorDiv = document.getElementById('auth-error');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
}

function hideError() {
    document.getElementById('auth-error').style.display = 'none';
}

function clearDashboard() {
    // Clear chat
    const chatContainer = document.getElementById('chat-container');
    chatContainer.innerHTML = `
        <div class="chat-welcome">
            <div class="welcome-icon">💡</div>
            <h3>Ready to answer your questions</h3>
            <p>Upload documents and ask questions about their content</p>
        </div>
    `;

    // Clear upload status
    const uploadStatus = document.getElementById('upload-status');
    uploadStatus.style.display = 'none';
    uploadStatus.className = 'upload-status';
    uploadStatus.textContent = '';
}

// File upload functions
function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        handleFileUpload(file);
    }
}

async function handleFileUpload(file) {
    const uploadStatus = document.getElementById('upload-status');
    uploadStatus.style.display = 'block';
    uploadStatus.className = 'upload-status loading';
    uploadStatus.innerHTML = '⏳ Uploading and processing...';

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(`${API_BASE}/upload`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`
            },
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Upload failed');
        }

        const data = await response.json();
        uploadStatus.className = 'upload-status success';
        uploadStatus.innerHTML = `
            ✅ <strong>${data.filename}</strong> uploaded successfully!<br>
            Created ${data.chunks_created} chunks for processing.
        `;

        // Clear file input
        document.getElementById('file-input').value = '';

        // Reload documents list
        loadDocuments();
    } catch (error) {
        uploadStatus.className = 'upload-status error';
        uploadStatus.innerHTML = `❌ ${error.message}`;
    }
}

// Query functions
async function handleQuery(e) {
    e.preventDefault();

    const queryInput = document.getElementById('query-input');
    const query = queryInput.value.trim();

    if (!query) return;

    // Clear input
    queryInput.value = '';

    // Remove welcome message if present
    const chatContainer = document.getElementById('chat-container');
    const welcome = chatContainer.querySelector('.chat-welcome');
    if (welcome) {
        welcome.remove();
    }

    // Add user message
    addMessage('user', query);

    // Add loading message
    const loadingId = 'loading-' + Date.now();
    addMessage('assistant', '⏳ Thinking...', loadingId);

    try {
        const response = await fetch(`${API_BASE}/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({ query, k: 4 })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Query failed');
        }

        const data = await response.json();

        // Remove loading message
        document.getElementById(loadingId)?.remove();

        // Add assistant response
        addMessage('assistant', data.answer, null, data.sources);
    } catch (error) {
        // Remove loading message
        document.getElementById(loadingId)?.remove();

        // Show error message
        addMessage('assistant', `❌ Error: ${error.message}`);
    }
}

function addMessage(role, content, id = null, sources = null) {
    const chatContainer = document.getElementById('chat-container');

    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message message-${role}`;
    if (id) messageDiv.id = id;

    const label = role === 'user' ? 'You' : 'AI Assistant';

    let html = `
        <div class="message-label">${label}</div>
        <div class="message-content">${escapeHtml(content)}</div>
    `;

    if (sources && sources.length > 0) {
        html += '<div class="message-sources"><h4>Sources</h4>';
        sources.forEach((source, index) => {
            const filename = source.metadata.filename || 'Unknown';
            const preview = source.content.substring(0, 150) + '...';
            html += `
                <div class="source-item">
                    <div class="source-content">"${escapeHtml(preview)}"</div>
                    <div class="source-meta">From: ${escapeHtml(filename)}</div>
                </div>
            `;
        });
        html += '</div>';
    }

    messageDiv.innerHTML = html;
    chatContainer.appendChild(messageDiv);

    // Scroll to bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Document history functions
async function loadDocuments() {
    try {
        const response = await fetch(`${API_BASE}/history/documents`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        if (!response.ok) {
            throw new Error('Failed to load documents');
        }

        const documents = await response.json();
        displayDocuments(documents);
    } catch (error) {
        console.error('Error loading documents:', error);
    }
}

function displayDocuments(documents) {
    const documentsList = document.getElementById('documents-list');

    if (documents.length === 0) {
        documentsList.innerHTML = '<div class="empty-state">No documents uploaded yet</div>';
        return;
    }

    documentsList.innerHTML = documents.map(doc => {
        const date = new Date(doc.uploaded_at).toLocaleDateString();
        const size = doc.file_size ? `${(doc.file_size / 1024).toFixed(1)} KB` : 'N/A';

        return `
            <div class="document-item">
                <div class="document-name">${escapeHtml(doc.filename)}</div>
                <div class="document-meta">${date} · ${size} · ${doc.chunks_created || 0} chunks</div>
            </div>
        `;
    }).join('');
}
