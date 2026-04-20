// Main JavaScript for AI Content Generator

const generateBtn = document.getElementById('generateBtn');
const researchBtn = document.getElementById('researchBtn');
const topicInput = document.getElementById('topic');
const resultsSection = document.getElementById('results');
const researchResults = document.getElementById('researchResults');
const errorBox = document.getElementById('error');
const loadingProgress = document.getElementById('loadingProgress');
const themeToggle = document.getElementById('themeToggle');

// Store recommended topic globally
let currentRecommendedTopic = '';

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

// Research topics on button click
researchBtn.addEventListener('click', researchTopics);

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
    researchResults.style.display = 'none';
    loadingProgress.style.display = 'none';
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
    
    // Focus on input
    topicInput.focus();
}

async function researchTopics() {
    // Hide previous results and errors
    resultsSection.style.display = 'none';
    researchResults.style.display = 'none';
    errorBox.style.display = 'none';
    
    // Show loading progress
    loadingProgress.style.display = 'block';
    researchBtn.disabled = true;
    generateBtn.disabled = true;
    
    // Reset all cards
    resetCards();
    
    // Animate cards sequentially
    animateCards();
    
    try {
        const response = await fetch('/research', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                keywords: [
                    'AI automation business',
                    'make money online',
                    'digital marketing tips',
                    'entrepreneur advice',
                    'business growth'
                ]
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Research failed');
        }
        
        const data = await response.json();
        
        // Wait for all cards to complete
        await sleep(8000);
        
        // Display research results
        displayResearchResults(data);
        
    } catch (error) {
        showError('Research failed: ' + error.message);
        console.error('Error:', error);
        loadingProgress.style.display = 'none';
    } finally {
        researchBtn.disabled = false;
        generateBtn.disabled = false;
    }
}

function displayResearchResults(data) {
    // Hide loading
    loadingProgress.style.display = 'none';
    
    // Show research results section
    researchResults.style.display = 'block';
    
    // Check for warnings
    if (data.warning) {
        showError(data.warning);
        return;
    }
    
    // Display timestamp
    document.getElementById('researchTimestamp').textContent = 
        `Analyzed at ${new Date().toLocaleString()}`;
    
    // Display source information and mode
    const sourceInfo = document.getElementById('sourceInfo');
    const primarySource = data.primary_source || 'unknown';
    const instagramCount = data.instagram_posts || 0;
    const youtubeCount = data.youtube_posts || 0;
    const mode = data.mode || 'unknown';
    
    let sourceHTML = '<div class="source-stats">';
    
    // Display mode badge
    if (mode === 'instagram_only') {
        sourceHTML += `<span class="mode-badge render">🚀 Render Mode: Instagram Only</span>`;
    } else if (mode === 'instagram_and_youtube') {
        sourceHTML += `<span class="mode-badge local">💻 Local Mode: Instagram + YouTube</span>`;
    }
    
    // Display source info
    if (primarySource === 'instagram') {
        sourceHTML += `
            <span class="source-badge-large primary">📸 Instagram Primary</span>
            <span class="source-count">${instagramCount} Instagram posts</span>
        `;
        if (youtubeCount > 0) {
            sourceHTML += `<span class="source-count secondary">${youtubeCount} YouTube posts (backup)</span>`;
        }
    } else if (primarySource === 'youtube') {
        sourceHTML += `
            <span class="source-badge-large backup">📺 YouTube Backup</span>
            <span class="source-count">${youtubeCount} YouTube posts</span>
        `;
    }
    
    sourceHTML += '</div>';
    sourceInfo.innerHTML = sourceHTML;
    
    // Display recommended topic
    if (data.recommended_topic) {
        currentRecommendedTopic = data.recommended_topic.keyword;
        document.getElementById('recommendedKeyword').textContent = 
            data.recommended_topic.keyword.toUpperCase();
        document.getElementById('recommendedReason').textContent = 
            data.recommended_topic.reason;
    }
    
    // Display top topics table
    const topicsTable = document.getElementById('topicsTable');
    let tableHTML = `
        <table>
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Topic</th>
                    <th>Score</th>
                    <th>Posts</th>
                    <th>Avg ER</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    data.top_topics.forEach(topic => {
        tableHTML += `
            <tr>
                <td><span class="rank-badge">#${topic.rank}</span></td>
                <td><strong>${topic.keyword}</strong></td>
                <td>${topic.avg_score.toFixed(2)}</td>
                <td>${topic.post_count}</td>
                <td>${topic.avg_engagement_rate}%</td>
                <td>
                    <button class="use-btn" onclick="useTopic('${topic.keyword}')">
                        <i class="fas fa-magic"></i> Use
                    </button>
                </td>
            </tr>
        `;
    });
    
    tableHTML += `
            </tbody>
        </table>
    `;
    
    topicsTable.innerHTML = tableHTML;
    
    // Display stats
    document.getElementById('totalAnalyzed').textContent = data.total_analyzed;
    document.getElementById('passedFilters').textContent = data.passed_filters;
    document.getElementById('viralFlag').textContent = 
        data.repeat_viral_flag ? '🔥 YES' : 'No';
    
    // Scroll to results
    researchResults.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function useRecommendedTopic() {
    if (currentRecommendedTopic) {
        topicInput.value = currentRecommendedTopic;
        
        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
        
        // Highlight input
        topicInput.focus();
        topicInput.select();
        
        // Show feedback
        showSuccess('Topic loaded! Click "Generate Magic" to create content.');
    }
}

function useTopic(keyword) {
    topicInput.value = keyword;
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
    
    // Highlight input
    topicInput.focus();
    topicInput.select();
    
    // Show feedback
    showSuccess('Topic loaded! Click "Generate Magic" to create content.');
}

function showSuccess(message) {
    const successBox = document.createElement('div');
    successBox.className = 'success-box glass-card';
    successBox.innerHTML = '<i class="fas fa-check-circle"></i> ' + message;
    successBox.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 1000;
        padding: 15px 20px;
        background: rgba(76, 175, 80, 0.2);
        border: 1px solid rgba(76, 175, 80, 0.5);
        border-radius: 12px;
        color: #4caf50;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(successBox);
    
    setTimeout(() => {
        successBox.remove();
    }, 3000);
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
