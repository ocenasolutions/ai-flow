// Main JavaScript for AI Content Generator

const generateBtn = document.getElementById('generateBtn');
const topicInput = document.getElementById('topic');
const resultsSection = document.getElementById('results');
const errorBox = document.getElementById('error');
const loadingProgress = document.getElementById('loadingProgress');

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
    loadingProgress.style.display = 'grid';
    generateBtn.disabled = true;
    
    // Animate progress steps
    await animateProgress();
    
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
        
        // Complete all steps
        completeAllSteps();
        
        // Wait a bit before showing results
        await sleep(500);
        
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

async function animateProgress() {
    const steps = ['step1', 'step2', 'step3', 'step4'];
    
    for (let i = 0; i < steps.length; i++) {
        const step = document.getElementById(steps[i]);
        step.classList.add('active');
        
        // Simulate processing time
        await sleep(i === 0 ? 500 : 1000);
        
        // Mark as completed
        step.classList.remove('active');
        step.classList.add('completed');
        step.querySelector('.progress-status').textContent = '✅';
    }
}

function completeAllSteps() {
    const steps = ['step1', 'step2', 'step3', 'step4'];
    steps.forEach(stepId => {
        const step = document.getElementById(stepId);
        step.classList.remove('active');
        step.classList.add('completed');
        step.querySelector('.progress-status').textContent = '✅';
    });
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
        const btn = event.target.closest('.copy-btn');
        const originalHTML = btn.innerHTML;
        btn.innerHTML = '<span class="copy-icon">✓</span> Copied!';
        btn.style.background = 'linear-gradient(135deg, #4caf50 0%, #45a049 100%)';
        
        setTimeout(() => {
            btn.innerHTML = originalHTML;
            btn.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
        }, 2000);
    }).catch(err => {
        showError('Failed to copy to clipboard');
        console.error('Copy error:', err);
    });
}

function resetForm() {
    // Reset progress cards
    const steps = ['step1', 'step2', 'step3', 'step4'];
    steps.forEach(stepId => {
        const step = document.getElementById(stepId);
        step.classList.remove('active', 'completed');
        step.querySelector('.progress-status').textContent = '⏳';
    });
    
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
