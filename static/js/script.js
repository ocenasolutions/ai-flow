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

// Platform selection state
let selectedPlatforms = ['instagram', 'twitter']; // Default: Instagram + Twitter

// Initialize platform selectors
document.addEventListener('DOMContentLoaded', () => {
    const platformBadges = document.querySelectorAll('.source-badge.selectable');
    
    platformBadges.forEach(badge => {
        badge.addEventListener('click', () => {
            const platform = badge.dataset.platform;
            
            if (badge.classList.contains('active')) {
                // Deselect
                badge.classList.remove('active');
                selectedPlatforms = selectedPlatforms.filter(p => p !== platform);
            } else {
                // Select
                badge.classList.add('active');
                if (!selectedPlatforms.includes(platform)) {
                    selectedPlatforms.push(platform);
                }
            }
            
            // Update research button text
            updateResearchButtonText();
        });
    });
    
    // Set initial state
    updateResearchButtonText();
});

function updateResearchButtonText() {
    const btnText = document.querySelector('.research-btn .btn-text');
    if (selectedPlatforms.length === 0) {
        btnText.textContent = 'Select at least one platform';
        researchBtn.disabled = true;
    } else {
        btnText.textContent = 'Research Trending Topics';
        researchBtn.disabled = false;
    }
}

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

function copyToClipboard(elementId, btnElement) {
    const element = document.getElementById(elementId);
    const text = element.textContent;
    
    navigator.clipboard.writeText(text).then(() => {
        // Show success feedback
        const btn = btnElement || window.event.target.closest('.copy-btn');
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
    // Check if at least one platform is selected
    if (selectedPlatforms.length === 0) {
        showError('Please select at least one platform to analyze');
        return;
    }
    
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
    
    // Start animation loop (will continue until API responds)
    let animationRunning = true;
    const animationPromise = loopCardAnimation(() => animationRunning);
    
    try {
        const response = await fetch('/research', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                platforms: selectedPlatforms,
                keywords: [
                    'AI automation business',
                    'make money online',
                    'digital marketing tips',
                    'entrepreneur advice',
                    'business growth'
                ]
            })
        });
        
        // Stop animation loop
        animationRunning = false;
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Research failed');
        }
        
        const data = await response.json();
        
        // Wait a moment for final card animation to complete
        await sleep(2000);
        
        // Display research results
        displayResearchResults(data);
        
    } catch (error) {
        animationRunning = false;
        showError('Research failed: ' + error.message);
        console.error('Error:', error);
        loadingProgress.style.display = 'none';
    } finally {
        researchBtn.disabled = false;
        generateBtn.disabled = false;
    }
}

async function loopCardAnimation(isRunning) {
    while (isRunning()) {
        await animateCards();
        // Small pause before restarting loop
        await sleep(500);
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
    
    // Display source information
    const sourceInfo = document.getElementById('sourceInfo');
    const instagramCount = data.instagram_posts || 0;
    const twitterCount = data.twitter_posts || 0;
    const youtubeCount = data.youtube_posts || 0;
    const totalPosts = instagramCount + twitterCount + youtubeCount;
    const platformsUsed = data.platforms_used || [];
    
    let sourceHTML = '<div class="source-stats">';
    sourceHTML += `<div class="source-summary">Analyzed ${totalPosts} viral posts from ${platformsUsed.length} platform(s):</div>`;
    
    if (platformsUsed.includes('instagram') && instagramCount > 0) {
        sourceHTML += `<span class="source-badge-large instagram"><i class="fab fa-instagram"></i> ${instagramCount} Instagram Reels</span>`;
    }
    if (platformsUsed.includes('twitter') && twitterCount > 0) {
        sourceHTML += `<span class="source-badge-large twitter"><i class="fab fa-twitter"></i> ${twitterCount} Tweets</span>`;
    }
    if (platformsUsed.includes('youtube') && youtubeCount > 0) {
        sourceHTML += `<span class="source-badge-large youtube"><i class="fab fa-youtube"></i> ${youtubeCount} YouTube Shorts</span>`;
    }
    
    // Show message if no posts from selected platforms
    if (totalPosts === 0) {
        sourceHTML += `<p class="no-posts">No posts found from selected platforms. Try different platforms or check your configuration.</p>`;
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
    
    // Display viral posts with links
    const postsGrid = document.getElementById('postsGrid');
    let postsHTML = '';
    
    if (data.viral_posts && data.viral_posts.length > 0) {
        data.viral_posts.slice(0, 12).forEach(post => {
            const platformIcon = post.platform === 'instagram' ? 'fa-instagram' : 
                                 post.platform === 'twitter' ? 'fa-twitter' : 'fa-youtube';
            const platformColor = post.platform === 'instagram' ? '#E4405F' : 
                                  post.platform === 'twitter' ? '#1DA1F2' : '#FF0000';
            
            postsHTML += `
                <div class="post-card">
                    <div class="post-header">
                        <i class="fab ${platformIcon}" style="color: ${platformColor}"></i>
                        <span class="post-username">@${post.username || 'unknown'}</span>
                    </div>
                    <div class="post-content">
                        <p class="post-title">${post.title || post.caption || 'No caption'}</p>
                    </div>
                    <div class="post-stats">
                        <span><i class="fas fa-eye"></i> ${formatNumber(post.views)}</span>
                        <span><i class="fas fa-heart"></i> ${formatNumber(post.likes)}</span>
                        <span><i class="fas fa-chart-line"></i> ${post.engagement_rate}%</span>
                    </div>
                    <a href="${post.url}" target="_blank" class="post-link">
                        <i class="fas fa-external-link-alt"></i> View Post
                    </a>
                </div>
            `;
        });
    } else {
        postsHTML = '<p class="no-posts">No viral posts found from selected platforms</p>';
    }
    
    postsGrid.innerHTML = postsHTML;
    
    // Display stats
    document.getElementById('totalAnalyzed').textContent = data.total_analyzed;
    document.getElementById('passedFilters').textContent = data.passed_filters;
    document.getElementById('viralFlag').textContent = 
        data.repeat_viral_flag ? '🔥 YES' : 'No';
    
    // Scroll to results
    researchResults.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
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
