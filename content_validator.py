#!/usr/bin/env python3
"""
AGENT 02 - Content Validator
Analyzes scraped content and identifies top trending topics
Customized for Web Dev, App Dev, AI Automation, Tech Consulting niche
"""

from collections import defaultdict
import re

# Niche-specific keyword clusters
WEB_DEV = ["website", "web", "landing", "design", "frontend", "wordpress", "shopify", "site", "page", "html", "css"]
APP_DEV = ["app", "mobile", "android", "ios", "flutter", "software", "saas", "application", "development"]
AI_AUTO = ["automation", "ai", "claude", "chatgpt", "workflow", "n8n", "zapier", "automate", "artificial", "intelligence"]
CONSULTING = ["consultant", "agency", "client", "project", "freelance", "business", "revenue", "consulting", "service"]

CLUSTER_NAMES = {
    'web_dev': 'Web Development',
    'app_dev': 'App Development',
    'ai_auto': 'AI Automation',
    'consulting': 'Tech Consulting'
}

# Global variable to store validation results
validation_results = {}


def calculate_scores(posts):
    """
    Calculate normalized scores for each post
    
    Args:
        posts: List of post dicts from content_scraper
    
    Returns:
        List of posts with added score fields
    """
    if not posts:
        return []
    
    # Find max values for normalization
    max_views = max(p['views'] for p in posts) if posts else 1
    max_er = max(p['engagement_rate'] for p in posts) if posts else 1
    max_comments = max(p['comments'] for p in posts) if posts else 1
    
    # Avoid division by zero
    max_views = max_views if max_views > 0 else 1
    max_er = max_er if max_er > 0 else 1
    max_comments = max_comments if max_comments > 0 else 1
    
    scored_posts = []
    
    for post in posts:
        # Calculate weighted scores
        views_score = (post['views'] / max_views) * 40
        engagement_score = (post['engagement_rate'] / max_er) * 35
        comments_score = (post['comments'] / max_comments) * 25
        
        total_score = views_score + engagement_score + comments_score
        
        # Add scores to post
        post_with_scores = post.copy()
        post_with_scores['views_score'] = round(views_score, 2)
        post_with_scores['engagement_score'] = round(engagement_score, 2)
        post_with_scores['comments_score'] = round(comments_score, 2)
        post_with_scores['total_score'] = round(total_score, 2)
        
        scored_posts.append(post_with_scores)
    
    return scored_posts


def filter_posts(posts):
    """
    Filter out low-performing posts
    
    Args:
        posts: List of scored posts
    
    Returns:
        Filtered list of posts
    """
    filtered = []
    
    for post in posts:
        # Filter criteria
        if post['views'] < 10000:
            continue
        if post['engagement_rate'] < 2.0:
            continue
        
        filtered.append(post)
    
    return filtered


def extract_keywords(text):
    """
    Extract meaningful keywords from title/caption
    
    Args:
        text: Title or caption text
    
    Returns:
        List of keywords
    """
    if not text:
        return []
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters but keep spaces
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    
    # Common stop words to ignore
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'be', 'been',
        'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we',
        'they', 'my', 'your', 'his', 'her', 'its', 'our', 'their', 'me', 'him',
        'them', 'what', 'which', 'who', 'when', 'where', 'why', 'how', 'all',
        'each', 'every', 'both', 'few', 'more', 'most', 'some', 'such', 'no',
        'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'can', 'will',
        'just', 'should', 'now', 'get', 'got', 'have', 'has', 'had', 'do', 'does',
        'did', 'make', 'made', 'go', 'went', 'see', 'saw', 'know', 'knew'
    }
    
    # Split into words
    words = text.split()
    
    # Filter out stop words and short words
    keywords = [w for w in words if len(w) > 3 and w not in stop_words]
    
    return keywords


def classify_post_cluster(text):
    """
    Classify post into one of the 4 niche clusters
    
    Args:
        text: Title or caption text
    
    Returns:
        Cluster key ('web_dev', 'app_dev', 'ai_auto', 'consulting', or None)
    """
    if not text:
        return None
    
    text_lower = text.lower()
    
    # Count matches for each cluster
    scores = {
        'web_dev': sum(1 for keyword in WEB_DEV if keyword in text_lower),
        'app_dev': sum(1 for keyword in APP_DEV if keyword in text_lower),
        'ai_auto': sum(1 for keyword in AI_AUTO if keyword in text_lower),
        'consulting': sum(1 for keyword in CONSULTING if keyword in text_lower)
    }
    
    # Return cluster with highest score, or None if no matches
    max_score = max(scores.values())
    if max_score == 0:
        return None
    
    return max(scores, key=scores.get)


def group_by_topic(posts):
    """
    Group posts by niche-specific clusters
    
    Args:
        posts: List of filtered posts
    
    Returns:
        Dict of topics with their posts and stats
    """
    # Initialize all 4 clusters with empty data
    cluster_posts = {
        'web_dev': [],
        'app_dev': [],
        'ai_auto': [],
        'consulting': []
    }
    
    # Classify each post
    for post in posts:
        text = post.get('title', '') + ' ' + post.get('caption', '')
        cluster = classify_post_cluster(text)
        
        if cluster:
            cluster_posts[cluster].append(post)
    
    # Calculate stats for each cluster
    topics = {}
    
    for cluster_key, posts_list in cluster_posts.items():
        if len(posts_list) > 0:
            avg_score = sum(p['total_score'] for p in posts_list) / len(posts_list)
            total_views = sum(p['views'] for p in posts_list)
            avg_er = sum(p['engagement_rate'] for p in posts_list) / len(posts_list)
        else:
            avg_score = 0
            total_views = 0
            avg_er = 0
        
        topics[cluster_key] = {
            'keyword': CLUSTER_NAMES[cluster_key],
            'post_count': len(posts_list),
            'avg_score': round(avg_score, 2),
            'total_views': total_views,
            'avg_engagement_rate': round(avg_er, 2),
            'posts': posts_list
        }
    
    return topics


def get_top_topics(topics, limit=4):
    """
    Get all 4 niche clusters ranked by average score
    Always returns all 4 clusters even if some have 0 posts
    
    Args:
        topics: Dict of topics
        limit: Number of top topics to return (default 4 for our clusters)
    
    Returns:
        List of all 4 topics sorted by avg_score
    """
    # Sort by average score (descending)
    sorted_topics = sorted(
        topics.values(),
        key=lambda x: x['avg_score'],
        reverse=True
    )
    
    return sorted_topics  # Return all 4 clusters


def validate_content(scraped_data):
    """
    Main validation function
    
    Args:
        scraped_data: List of posts from content_scraper
    
    Returns:
        Dict with validation results
    """
    global validation_results
    
    print("\n🔍 Starting content validation...")
    
    # Step 1: Calculate scores
    print("📊 Calculating scores...")
    scored_posts = calculate_scores(scraped_data)
    
    # Step 2: Filter posts
    print("🔎 Filtering low-performing content...")
    filtered_posts = filter_posts(scored_posts)
    print(f"✅ {len(filtered_posts)} posts passed filters")
    
    if not filtered_posts:
        validation_results = {
            'error': 'No posts met the minimum criteria (10K views, 2% ER)',
            'total_analyzed': len(scraped_data),
            'passed_filters': 0
        }
        return validation_results
    
    # Step 3: Group by niche-specific clusters
    print("🏷️  Grouping by niche clusters...")
    topics = group_by_topic(filtered_posts)
    
    # Step 4: Get all 4 clusters ranked
    top_topics = get_top_topics(topics, limit=4)
    
    # Step 5: Identify recommended topic (highest scoring cluster with posts)
    recommended_topic = None
    for topic in top_topics:
        if topic['post_count'] > 0:
            recommended_topic = topic
            break
    
    # Step 6: Check for repeat viral signals
    repeat_viral_flag = any(topic['post_count'] >= 3 for topic in top_topics)
    
    # Build results
    validation_results = {
        'total_analyzed': len(scraped_data),
        'passed_filters': len(filtered_posts),
        'top_topics': [
            {
                'rank': i + 1,
                'keyword': topic['keyword'],
                'post_count': topic['post_count'],
                'avg_score': topic['avg_score'],
                'total_views': topic['total_views'],
                'avg_engagement_rate': topic['avg_engagement_rate']
            }
            for i, topic in enumerate(top_topics)
        ],
        'recommended_topic': {
            'keyword': recommended_topic['keyword'],
            'reason': f"Highest average score ({recommended_topic['avg_score']}) across {recommended_topic['post_count']} posts with {recommended_topic['total_views']:,} total views",
            'avg_score': recommended_topic['avg_score'],
            'post_count': recommended_topic['post_count']
        } if recommended_topic else {
            'keyword': 'No recommendation',
            'reason': 'Not enough data to recommend a topic',
            'avg_score': 0,
            'post_count': 0
        },
        'repeat_viral_flag': repeat_viral_flag,
        'repeat_viral_message': '🔥 Multiple topics have 3+ viral posts - strong trend detected!' if repeat_viral_flag else None
    }
    
    print("\n✅ Validation complete!")
    if recommended_topic:
        print(f"🏆 Recommended topic: {validation_results['recommended_topic']['keyword']}")
    
    return validation_results


# For testing
if __name__ == '__main__':
    # Mock data for testing
    mock_data = [
        {
            'platform': 'youtube',
            'title': 'AI automation for small business owners',
            'caption': '',
            'views': 150000,
            'likes': 8000,
            'comments': 500,
            'engagement_rate': 5.67,
            'viral': True
        },
        {
            'platform': 'instagram',
            'title': 'How to automate your business with AI',
            'caption': 'AI automation tips for entrepreneurs',
            'views': 80000,
            'likes': 4000,
            'comments': 300,
            'engagement_rate': 5.38,
            'viral': True
        },
        {
            'platform': 'youtube',
            'title': 'Make money online with automation',
            'caption': '',
            'views': 120000,
            'likes': 6000,
            'comments': 400,
            'engagement_rate': 5.33,
            'viral': True
        },
        {
            'platform': 'instagram',
            'title': 'Business automation secrets',
            'caption': 'Automate everything in your business',
            'views': 50000,
            'likes': 2000,
            'comments': 150,
            'engagement_rate': 4.30,
            'viral': False
        },
        {
            'platform': 'youtube',
            'title': 'AI tools for entrepreneurs',
            'caption': '',
            'views': 30000,
            'likes': 1500,
            'comments': 100,
            'engagement_rate': 5.33,
            'viral': True
        }
    ]
    
    results = validate_content(mock_data)
    
    print("\n" + "="*60)
    print("VALIDATION RESULTS:")
    print("="*60)
    print(f"\nTotal Analyzed: {results['total_analyzed']}")
    print(f"Passed Filters: {results['passed_filters']}")
    print(f"\nTop 5 Topics:")
    for topic in results['top_topics']:
        print(f"  {topic['rank']}. {topic['keyword']} - Score: {topic['avg_score']} ({topic['post_count']} posts)")
    
    if results['recommended_topic']:
        print(f"\n🏆 RECOMMENDED: {results['recommended_topic']['keyword']}")
        print(f"   Reason: {results['recommended_topic']['reason']}")
    
    if results['repeat_viral_flag']:
        print(f"\n{results['repeat_viral_message']}")
