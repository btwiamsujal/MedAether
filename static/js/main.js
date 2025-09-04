// MedAether Main JavaScript Functions

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    const popoverList = popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        setTimeout(() => {
            card.classList.add('fade-in');
        }, index * 100);
    });
    
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});

// Utility Functions

function showLoading() {
    const spinner = document.createElement('div');
    spinner.className = 'spinner-overlay';
    spinner.innerHTML = `
        <div class="spinner-border spinner-border-xl text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
        </div>
    `;
    document.body.appendChild(spinner);
}

function hideLoading() {
    const spinner = document.querySelector('.spinner-overlay');
    if (spinner) {
        spinner.remove();
    }
}

function showNotification(message, type = 'info') {
    const alertContainer = document.createElement('div');
    alertContainer.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertContainer.style.cssText = 'top: 20px; right: 20px; z-index: 1055; min-width: 300px;';
    alertContainer.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertContainer);
    
    // Auto-remove after 4 seconds
    setTimeout(() => {
        if (alertContainer.parentNode) {
            alertContainer.remove();
        }
    }, 4000);
}

// Health-related Functions

function getHealthStatusColor(status) {
    switch(status) {
        case 'green': return '#198754';
        case 'yellow': return '#ffc107';
        case 'red': return '#dc3545';
        default: return '#6c757d';
    }
}

function getHealthStatusText(status) {
    switch(status) {
        case 'green': return 'Healthy';
        case 'yellow': return 'Moderate Issues';
        case 'red': return 'Attention Needed';
        default: return 'Unknown';
    }
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

function formatTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Voice Recognition Functions

function initializeVoiceRecognition(inputElementId, callback) {
    if (!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
        console.warn('Speech recognition not supported in this browser');
        return null;
    }
    
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';
    
    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        const inputElement = document.getElementById(inputElementId);
        if (inputElement) {
            inputElement.value = transcript;
        }
        if (callback) callback(transcript);
    };
    
    recognition.onerror = function(event) {
        console.error('Speech recognition error:', event.error);
        showNotification('Voice recognition failed. Please try again.', 'warning');
    };
    
    return recognition;
}

// Language Translation Functions

function translateText(text, targetLanguage) {
    return fetch('/translate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            text: text,
            target_language: targetLanguage
        })
    })
    .then(response => response.json())
    .then(data => data.translated_text)
    .catch(error => {
        console.error('Translation error:', error);
        return text; // Return original text if translation fails
    });
}

// Form Validation Functions

function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validatePhone(phone) {
    const re = /^[\+]?[1-9][\d]{0,15}$/;
    return re.test(phone.replace(/\s/g, ''));
}

function validatePassword(password) {
    return password.length >= 6;
}

// Health Card Functions

function generateHealthCardQR(userData) {
    const qrData = {
        name: userData.name,
        age: userData.age,
        gender: userData.gender,
        health_status: userData.health_status,
        emergency_contact: userData.emergency_contact || 'Not provided',
        medical_history: userData.medical_history || [],
        generated: new Date().toISOString()
    };
    
    return JSON.stringify(qrData);
}

function downloadHealthCard() {
    const healthCard = document.querySelector('.health-card');
    if (!healthCard) return;
    
    // Create print-friendly version
    const printWindow = window.open('', '_blank');
    const styles = `
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .card { border: 3px solid #000; border-radius: 15px; overflow: hidden; }
            .card-header { background-color: #0d6efd; color: white; padding: 20px; }
            .card-body { padding: 20px; }
            .health-status { font-size: 1.2em; font-weight: bold; }
            @media print { 
                body { margin: 0; }
                .no-print { display: none; }
            }
        </style>
    `;
    
    printWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>MedAether Health Card</title>
            ${styles}
        </head>
        <body>
            ${healthCard.outerHTML}
            <div class="text-center mt-3">
                <small>Generated on ${new Date().toLocaleDateString()}</small>
            </div>
        </body>
        </html>
    `);
    
    printWindow.document.close();
    setTimeout(() => printWindow.print(), 500);
}

// API Functions

async function makeAPIRequest(url, method = 'GET', data = null) {
    const config = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        }
    };
    
    if (data) {
        config.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(url, config);
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.message || 'Request failed');
        }
        
        return result;
    } catch (error) {
        console.error('API request failed:', error);
        throw error;
    }
}

// Chat Functions

function scrollToBottom(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.scrollTop = element.scrollHeight;
    }
}

function addChatMessage(container, message, sender, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'mb-3';
    
    const timestamp = new Date().toLocaleString();
    const alignClass = isUser ? 'justify-content-end' : 'justify-content-start';
    const bgClass = isUser ? 'bg-primary text-white' : 'bg-light';
    
    messageDiv.innerHTML = `
        <div class="d-flex ${alignClass}">
            <div class="${bgClass} p-3 rounded-3" style="max-width: 70%;">
                <strong>${sender}:</strong> ${message}
                <div class="small ${isUser ? 'text-light' : 'text-muted'} mt-1">${timestamp}</div>
            </div>
        </div>
    `;
    
    container.appendChild(messageDiv);
    scrollToBottom(container.id);
}

// Local Storage Functions

function saveToLocalStorage(key, data) {
    try {
        localStorage.setItem(key, JSON.stringify(data));
    } catch (error) {
        console.error('Failed to save to localStorage:', error);
    }
}

function getFromLocalStorage(key) {
    try {
        const data = localStorage.getItem(key);
        return data ? JSON.parse(data) : null;
    } catch (error) {
        console.error('Failed to retrieve from localStorage:', error);
        return null;
    }
}

function removeFromLocalStorage(key) {
    try {
        localStorage.removeItem(key);
    } catch (error) {
        console.error('Failed to remove from localStorage:', error);
    }
}

// Theme Functions

function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    saveToLocalStorage('theme', theme);
}

function getTheme() {
    return getFromLocalStorage('theme') || 'light';
}

function initializeTheme() {
    const savedTheme = getTheme();
    setTheme(savedTheme);
}

// Initialize theme on load
document.addEventListener('DOMContentLoaded', initializeTheme);

// Error Handling

window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
    // You could send error reports to a logging service here
});

window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled promise rejection:', e.reason);
    // You could send error reports to a logging service here
});

// Utility function for copying text to clipboard
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showNotification('Copied to clipboard!', 'success');
    } catch (error) {
        console.error('Failed to copy to clipboard:', error);
        showNotification('Failed to copy to clipboard', 'warning');
    }
}

// Function to format health data for display
function formatHealthData(data) {
    const formatted = {};
    
    for (const [key, value] of Object.entries(data)) {
        switch(key) {
            case 'blood_pressure':
                formatted[key] = value || 'Not recorded';
                break;
            case 'blood_sugar':
                formatted[key] = value ? `${value} mg/dL` : 'Not recorded';
                break;
            case 'body_temperature':
                formatted[key] = value ? `${value}°F` : 'Normal';
                break;
            case 'heart_rate':
                formatted[key] = value ? `${value} BPM` : 'Not recorded';
                break;
            case 'current_weight':
                formatted[key] = value ? `${value} kg` : 'Not set';
                break;
            default:
                formatted[key] = value;
        }
    }
    
    return formatted;
}

// Export functions for use in other modules
window.MedAether = {
    showLoading,
    hideLoading,
    showNotification,
    getHealthStatusColor,
    getHealthStatusText,
    formatDate,
    formatTime,
    initializeVoiceRecognition,
    translateText,
    validateEmail,
    validatePhone,
    validatePassword,
    generateHealthCardQR,
    downloadHealthCard,
    makeAPIRequest,
    scrollToBottom,
    addChatMessage,
    saveToLocalStorage,
    getFromLocalStorage,
    removeFromLocalStorage,
    setTheme,
    getTheme,
    copyToClipboard,
    formatHealthData
};
