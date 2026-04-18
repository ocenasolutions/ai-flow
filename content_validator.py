#!/usr/bin/env python3
"""
AGENT 02: CONTENT VALIDATOR
Scores, filters, and ranks scraped content to identify viral topics
"""

import pandas as pd
from collections import Counter
import re

def calculate_score(row):
    """Calculate viral score out of 100"""
    score = 0
    
    # Views score (40% weight)
    views = row['views']
    if views >= 1000000:
        score += 40
    elif views >= 500000:
        score += 35
    elif views >= 100000:
        score += 25
    elif views >= 10000:
        score += 15
    else:
        score += 0
    
    # Engagement rate score (35% weight)
    eng_rate = row['engagement_rate']
    if eng_rate >= 10:
        score += 35
    elif eng_rate >= 5:
        score += 28
    elif eng_rate >= 2:
        score += 15
    else:
        score += 0
    
    # Comment volume score (25% weight)
    comments = row['comments']
    if comments >= 5000:
        score += 25
    elif comments >= 1000:
        score += 18
    elif comments >= 100:
        score += 10
    else:
        score += 0
    
    return score

def assign_topic(text):
    """Assign topic category based on content"""
    text_lower = str(text).lower()
    
    if any(word in text_lower for word in ['tutorial', 'how to', 'guide', 'setup', 'install']):
        return 'AI Tool Tutorials'
    elif any(word in text_lower for word in ['money', 'income', 'revenue', 'profit', 'earn']):
        return 'Automation Income'
    elif any(word in text_lower for word in ['agent', 'workflow', 'n8n', 'automation setup']):
        return 'Agent Setup Walkthroughs'
    elif any(word in text_lower for word in ['vs', 'versus', 'better than', 'replace']):
        return 'AI vs Traditional Tools'
    elif any(word in text_lower for word in ['code', 'coding', 'programming', 'developer']):
        return 'Coding with AI'
    else:
        return 'Other'

def main():
    print("=" * 60)
    print("AGENT 02: CONTENT VALIDATOR")
    print("=" * 60)
    
    # Read scraped data
    try:
        df = pd.read_csv('content_scraper_output.csv')
    except FileNotFoundError:
        print("❌ content_scraper_output.csv not found. Run content_scraper.py first.")
        return
    
    print(f"\n📊 Loaded {len(df)} posts")
    
    # Calculate scores
    df['score'] = df.apply(calculate_score, axis=1)
    
    # Filter low-quality content
    df_filtered = df[
        (df['score'] >= 20) &
        (df['views'] >= 10000) &
        (df['engagement_rate'] >= 2)
    ].copy()
    
    print(f"✅ {len(df_filtered)} posts passed quality filter")
    
    if len(df_filtered) == 0:
        print("❌ No posts passed the filter. Try lowering thresholds.")
        return
    
    # Assign topics
    df_filtered['topic'] = df_filtered.apply(
        lambda row: assign_topic(row['title'] + ' ' + row['description']),
        axis=1
    )
    
    # Topic analysis
    topic_stats = df_filtered.groupby('topic').agg({
        'views': 'mean',
        'engagement_rate': 'mean',
        'score': 'mean'
    }).round(2)
    
    topic_stats = topic_stats.sort_values('views', ascending=False)
    
    # Count topic frequency
    topic_counts = Counter(df_filtered['topic'])
    
    # Identify repeat viral signals
    repeat_signals = [topic for topic, count in topic_counts.items() if count >= 3]
    
    # Get top recommendation
    if len(topic_stats) > 0:
        top_topic = topic_stats.index[0]
        top_views = topic_stats.loc[top_topic, 'views']
        top_engagement = topic_stats.loc[top_topic, 'engagement_rate']
        
        # Determine reason
        if topic_counts[top_topic] >= 3:
            reason = "Appears multiple times in top results (REPEAT VIRAL SIGNAL)"
        elif top_engagement > 8:
            reason = "Highest engagement rate"
        else:
            reason = "Highest average views"
    else:
        top_topic = "No clear winner"
        top_views = 0
        reason = "Insufficient data"
    
    # Save results
    df_filtered.to_csv('content_validator_output.csv', index=False)
    
    # Print summary
    print("\n" + "=" * 60)
    print("TOP 5 TOPICS BY AVERAGE VIEWS:")
    print("=" * 60)
    print(topic_stats.head(5).to_string())
    
    if repeat_signals:
        print("\n🔥 REPEAT VIRAL SIGNALS:")
        for topic in repeat_signals:
            print(f"   • {topic} (appeared {topic_counts[topic]} times)")
    
    print("\n" + "=" * 60)
    print(f"📌 RECOMMENDED TOPIC: {top_topic}")
    print(f"   Avg Views: {int(top_views):,}")
    print(f"   Reason: {reason}")
    print("=" * 60)
    
    print(f"\n✅ Saved validated results to content_validator_output.csv")

if __name__ == "__main__":
    main()
