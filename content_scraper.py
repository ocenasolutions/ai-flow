#!/usr/bin/env python3
"""
AGENT 01: CONTENT SCRAPER
Scrapes viral content from YouTube Shorts, Instagram Reels, and Twitter/X
"""

import pandas as pd
from datetime import datetime, timedelta
import subprocess
import json
import time
import random

def scrape_youtube_shorts():
    """Scrape YouTube Shorts using yt-dlp"""
    print("🎬 Scraping YouTube Shorts...")
    
    keywords = [
        "Claude Code", "AI agents", "N8N automation",
        "AI coding", "vibe coding", "AI automation"
    ]
    
    all_videos = []
    seven_days_ago = datetime.now() - timedelta(days=7)
    
    for keyword in keywords:
        try:
            # Search for shorts with yt-dlp
            search_query = f"ytsearch10:{keyword} shorts"
            cmd = [
                'yt-dlp',
                '--dump-json',
                '--skip-download',
                '--dateafter', seven_days_ago.strftime('%Y%m%d'),
                search_query
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            for line in result.stdout.strip().split('\n'):
                if line:
                    try:
                        video = json.loads(line)
                        all_videos.append({
                            'platform': 'YouTube',
                            'title': video.get('title', ''),
                            'views': video.get('view_count', 0),
                            'likes': video.get('like_count', 0),
                            'comments': video.get('comment_count', 0),
                            'upload_date': video.get('upload_date', ''),
                            'channel': video.get('uploader', ''),
                            'url': video.get('webpage_url', ''),
                            'description': video.get('description', '')[:200],
                            'transcript': video.get('subtitles', {})
                        })
                    except json.JSONDecodeError:
                        continue
            
            time.sleep(random.uniform(2, 4))  # Rate limiting
            
        except Exception as e:
            print(f"⚠️  YouTube error for '{keyword}': {str(e)}")
            continue
    
    print(f"✅ Found {len(all_videos)} YouTube Shorts")
    return all_videos

def scrape_instagram_reels():
    """Scrape Instagram Reels using instaloader"""
    print("📸 Scraping Instagram Reels...")
    
    # Read target accounts
    try:
        with open('iguser.txt', 'r') as f:
            accounts = [line.strip().replace('@', '') for line in f if line.strip()]
    except FileNotFoundError:
        print("⚠️  iguser.txt not found, skipping Instagram")
        return []
    
    all_reels = []
    seven_days_ago = datetime.now() - timedelta(days=7)
    
    for account in accounts:
        try:
            # Use instaloader CLI
            cmd = [
                'instaloader',
                '--no-pictures',
                '--no-videos',
                '--no-video-thumbnails',
                '--quiet',
                '--count=10',
                f':{account}'
            ]
            
            # Note: This is a simplified version. Full implementation would parse instaloader output
            print(f"  Checking @{account}...")
            time.sleep(random.uniform(3, 6))  # Rate limiting
            
        except Exception as e:
            print(f"⚠️  Instagram error for @{account}: {str(e)}")
            continue
    
    print(f"✅ Found {len(all_reels)} Instagram Reels")
    return all_reels

def scrape_twitter():
    """Scrape Twitter/X posts using snscrape"""
    print("🐦 Scraping Twitter/X...")
    
    keywords = [
        "Claude Code", "AI tools", "AI automation",
        "AI agents", "vibe coding"
    ]
    
    all_tweets = []
    seven_days_ago = datetime.now() - timedelta(days=7)
    
    for keyword in keywords:
        try:
            # snscrape command
            since_date = seven_days_ago.strftime('%Y-%m-%d')
            cmd = [
                'snscrape',
                '--jsonl',
                '--max-results', '20',
                f'twitter-search "{keyword} since:{since_date}"'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            for line in result.stdout.strip().split('\n'):
                if line:
                    try:
                        tweet = json.loads(line)
                        all_tweets.append({
                            'platform': 'Twitter',
                            'title': tweet.get('content', '')[:100],
                            'views': tweet.get('viewCount', 0),
                            'likes': tweet.get('likeCount', 0),
                            'comments': tweet.get('replyCount', 0),
                            'upload_date': tweet.get('date', ''),
                            'channel': tweet.get('user', {}).get('username', ''),
                            'url': tweet.get('url', ''),
                            'description': tweet.get('content', '')
                        })
                    except json.JSONDecodeError:
                        continue
            
            time.sleep(random.uniform(2, 4))
            
        except Exception as e:
            print(f"⚠️  Twitter error for '{keyword}': {str(e)}")
            continue
    
    print(f"✅ Found {len(all_tweets)} Tweets")
    return all_tweets

def main():
    print("=" * 60)
    print("AGENT 01: CONTENT SCRAPER")
    print("=" * 60)
    
    # Scrape all platforms
    youtube_data = scrape_youtube_shorts()
    instagram_data = scrape_instagram_reels()
    twitter_data = scrape_twitter()
    
    # Combine all data
    all_data = youtube_data + instagram_data + twitter_data
    
    if not all_data:
        print("\n❌ No data scraped. Check your internet connection and tool installations.")
        return
    
    # Create DataFrame
    df = pd.DataFrame(all_data)
    
    # Calculate engagement rate
    df['engagement_rate'] = ((df['likes'] + df['comments']) / df['views'].replace(0, 1)) * 100
    
    # Sort by views
    df = df.sort_values('views', ascending=False)
    
    # Add VIRAL tag
    df['viral_tag'] = df.apply(
        lambda row: 'VIRAL' if row['engagement_rate'] > 5 or row['views'] > 100000 else '',
        axis=1
    )
    
    # Save to CSV
    output_file = 'content_scraper_output.csv'
    df.to_csv(output_file, index=False)
    
    # Print top 10
    print("\n" + "=" * 60)
    print("TOP 10 RESULTS:")
    print("=" * 60)
    print(df[['platform', 'title', 'views', 'engagement_rate', 'viral_tag']].head(10).to_string(index=False))
    
    print(f"\n✅ Saved {len(df)} results to {output_file}")

if __name__ == "__main__":
    main()
