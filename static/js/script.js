// Main JavaScript for AI Content Generator

const generateBtn = document.getElementById('generateBtn');
const topicInput = document.getElementById('topic');
const resultsSection = document.getElementById('results');
const errorBox = document.getElementById('error');
const loadingProgress = document.getElementById('loadingProgress');
const themeToggle = document.getElementById('themeToggle');

// Theme Toggle
themeToggle.addEventListener('click', () => {
    const body = document.body;
    const icon = themeToggle.querySelector('i');
    
    if (body.classList.contains('light-theme')) {
        body.classList.remove('light-theme');
        body.classList.add('dark-theme');
        icon.classList.remove('fa-moon');
        icon.classList.add('fa-sun');
        localStorage.setItem('theme', 'dark');
    } else {
        body.classList.remove('dark-theme');
        body.classList.add('light-theme');
        icon.classList.remove('fa-sun');
        icon.classList.add('fa-moon');
        localStorage.setItem('theme', 'light');
    }
});

// Load saved theme
window.addEventListener('load', () => {
    const savedTheme = localStorage.getItem('theme') || 'light';
    const body = document.body;
    const icon = themeToggle.querySelector('i');
    
    if (savedTheme === 'dark') {
        body.classList.remove('light-theme');
        body.classList.add('dark-theme');
        icon.classList.remove('fa-moon');
        icon.classList.add('fa-sun');
    }
});

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
    
    // Hide previous results and errors
    resultsSection.style.display = 'none';
    errorBox.style.display = 'none';
    
    // Show loading progress
    loadingProgress.style.display = 'block';
    generateBtn.disabled = true;
    
    // Reset all cards
    resetCards();
    
    // Animate cards sequentially
    animateCards();
    
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
        
        // Wait for all cards to complete
        await sleep(8000);
        
        // Display results
        displayResults(data);
        
    } catch (error) {
        showError('Failed to generate content. Please check your API key and try again.');
        console.error('Error:', error);
        loadingProgress.style.display = 'none';
    } finally {
        generateBtn.disabled = false;
    }
}

function resetCards() {
    for (let i = 1; i <= 4; i++) {
        const card = document.getElementById(`card${i}`);
        card.classList.remove('active', 'flipped');
    }
}

async function animateCards() {
    for (let i = 1; i <= 4; i++) {
        const card = document.getElementById(`card${i}`);
        
        // Activate card
        card.classList.add('active');
        
        // Wait for processing
        await sleep(1500);
        
        // Flip card to show completion
        card.classList.remove('active');
        card.classList.add('flipped');
        
        // Small delay before next card
        await sleep(500);
    }
}

function displayResults(data) {
    // Hide loading
    loadingProgress.style.display = 'none';
    
    // Show results section
    resultsSection.style.display = 'block';
    
    // Display script
    document.getElementById('script').textContent = data.script;
    
    // Display hooks
    document.getElementById('hooks').textContent = data.hooks;
    
    // Display timestamp
    document.getElementById('timestamp').textContent = 
        `Generated at ${new Date().toLocaleString()}`;
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function showError(message) {
    errorBox.innerHTML = '<i class="fas fa-exclamation-triangle"></i> ' + message;
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
        const btn = event.target.closest('.copy-btn');
        const originalHTML = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-check"></i>';
        btn.style.background = 'rgba(76, 175, 80, 0.3)';
        btn.style.borderColor = '#4caf50';
        
        setTimeout(() => {
            btn.innerHTML = originalHTML;
            btn.style.background = 'rgba(255, 255, 255, 0.1)';
            btn.style.borderColor = 'rgba(255, 255, 255, 0.2)';
        }, 2000);
    }).catch(err => {
        showError('Failed to copy to clipboard');
        console.error('Copy error:', err);
    });
}

function resetForm() {
    // Reset cards
    resetCards();
    
    // Hide results
    resultsSection.style.display = 'none';
    loadingProgress.style.display = 'none';
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
    
    // Focus on input
    topicInput.focus();
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
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
