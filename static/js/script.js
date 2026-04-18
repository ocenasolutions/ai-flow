// Main JavaScript for AI Content Generator

const generateBtn = document.getElementById('generateBtn');
const topicInput = document.getElementById('topic');
const resultsSection = document.getElementById('results');
const errorBox = document.getElementById('error');
const loadingOverlay = document.getElementById('loading');

// Generate content on button click
generateBtn.addEventListener('click', generateContent);

// Allow Enter key to trigger generation
topicInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        generateContent();
    }
});

async function generateContent() {
    const topic = topicInput.value.trim();
    
    if (!topic) {
        showError('Please enter a topic');
        return;
    }
    
    // Show loading
    loadingOverlay.style.display = 'flex';
    resultsSection.style.display = 'none';
    errorBox.style.display = 'none';
    generateBtn.disabled = true;
    
    try {
        const response = await fetch('/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ topic: topic })
        });
        
        if (!response.ok) {
            throw new Error('Generation failed');
        }
        
        const data = await response.json();
        
        // Display results
        displayResults(data);
        
    } catch (error) {
        showError('Failed to generate content. Please check your API key and try again.');
        console.error('Error:', error);
    } finally {
        loadingOverlay.style.display = 'none';
        generateBtn.disabled = false;
    }
}

function displayResults(data) {
    // Show results section
    resultsSection.style.display = 'block';
    
    // Display script
    document.getElementById('script').textContent = data.script;
    
    // Display hooks
    document.getElementById('hooks').textContent = data.hooks;
    
    // Display timestamp
    document.getElementById('timestamp').textContent = 
        `✅ Generated at: ${new Date().toLocaleString()}`;
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function showError(message) {
    errorBox.textContent = '❌ ' + message;
    errorBox.style.display = 'block';
    
    // Hide error after 5 seconds
    setTimeout(() => {
        errorBox.style.display = 'none';
    }, 5000);
}

function copyToClipboard(elementId) {
    const element = document.getElementById(elementId);
    const text = element.textContent;
    
    navigator.clipboard.writeText(text).then(() => {
        // Show success feedback
        const btn = event.target;
        const originalText = btn.textContent;
        btn.textContent = '✓ Copied!';
        btn.style.background = '#4caf50';
        
        setTimeout(() => {
            btn.textContent = originalText;
            btn.style.background = '#667eea';
        }, 2000);
    }).catch(err => {
        showError('Failed to copy to clipboard');
        console.error('Copy error:', err);
    });
}

// Check server health on load
window.addEventListener('load', async () => {
    try {
        const response = await fetch('/health');
        if (!response.ok) {
            showError('Server connection issue');
        }
    } catch (error) {
        showError('Cannot connect to server');
    }
});
