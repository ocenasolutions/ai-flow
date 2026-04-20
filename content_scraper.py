#!/usr/bin/env python3
"""
AGENT 01 - Content Scraper
PRIMARY: Instagram via RapidAPI (2-step: user_id lookup → reels)
SECONDARY: Twitter/X via RapidAPI (search + user tweets)
BACKUP: YouTube Shorts with browser cookies (local only)
"""

import requests
from datetime import datetime, timedelta, timezone
import time
import os
from dotenv import load_dotenv

# Optional import for YouTube (only needed locally, not on Render)
try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False

# Load environment variables
load_dotenv()

# Global variable to store scraped data
scraped_data = []

# Twitter search queries for the niche
TWITTER_SEARCH_QUERIES = [
    "AI programming tutorial",
    "machine learning 2025",
    "software engineering tips",
    "web development nextjs",
    "AI tools developers"
]


def is_render_deployment():
    """Check if running on Render deployment"""
    return os.getenv('RENDER', '').lower() == 'true'


def get_user_id_from_username(username, rapidapi_key):
    """
    STEP 1: Get numeric user_id from Instagram username
    
    Args:
        username: Instagram username (without @)
        rapidapi_key: RapidAPI key
    
    Returns:
        user_id (string) or None if failed
    """
    try:
        url = "https://instagram-api-fast-reliable-data-scraper.p.rapidapi.com/user_id_by_username"
        
        headers = {
            "x-rapidapi-key": rapidapi_key,
            "x-rapidapi-host": "instagram-api-fast-reliable-data-scraper.p.rapidapi.com"
        }
        
        params = {"username": username}
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 429:
            print(f"      ⚠️  Rate limit reached")
            return None
        
        if response.status_code != 200:
            print(f"      ❌ API error ({response.status_code})")
            return None
        
        data = response.json()
        user_id = data.get('UserID') or data.get('user_id') or data.get('id')
        
        if user_id:
            print(f"      ✅ Got user_id: {user_id}")
            return str(user_id)
        else:
            print(f"      ❌ No user_id in response")
            return None
            
    except requests.exceptions.Timeout:
        print(f"      ❌ Request timeout")
        return None
    except Exception as e:
        print(f"      ❌ Error: {str(e)[:50]}")
        return None


def get_reels_from_user_id(user_id, username, rapidapi_key):
    """
    STEP 2: Get reels from user_id
    
    Args:
        user_id: Numeric Instagram user ID
        username: Username (for display)
        rapidapi_key: RapidAPI key
    
    Returns:
        List of reel dicts
    """
    reels_data = []
    
    try:
        url = "https://instagram-api-fast-reliable-data-scraper.p.rapidapi.com/reels"
        
        headers = {
            "x-rapidapi-key": rapidapi_key,
            "x-rapidapi-host": "instagram-api-fast-reliable-data-scraper.p.rapidapi.com"
        }
        
        params = {
            "user_id": user_id,
            "include_feed_video": "true"
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=15)
        
        if response.status_code == 429:
            print(f"      ⚠️  Rate limit reached")
            return reels_data
        
        if response.status_code != 200:
            print(f"      ❌ API error ({response.status_code})")
            return reels_data
        
        data = response.json()
        
        # Extract items from response
        items = data.get('data', {}).get('items', []) or data.get('items', [])
        
        if not items:
            print(f"      ⚠️  No reels found")
            return reels_data
        
        # Calculate date threshold (30 days ago)
        from datetime import timezone
        date_threshold = datetime.now(tz=timezone.utc) - timedelta(days=30)
        
        reel_count = 0
        
        for item in items:
            # Stop after 5 reels
            if reel_count >= 5:
                break
            
            try:
                # Handle both structures: item.media or item directly
                media = item.get("media", item)
                
                # Get code for URL
                code = media.get("code", "")
                if not code:
                    continue
                
                # Get timestamp
                taken_at = media.get("taken_at", 0)
                
                # Get caption
                caption_obj = media.get("caption") or {}
                caption = caption_obj.get("text", "") if isinstance(caption_obj, dict) else ""
                
                # Get metrics - try multiple field names
                likes = media.get("like_count") or media.get("likes") or 0
                comments = media.get("comment_count") or media.get("comments") or 0
                views = media.get("play_count") or media.get("view_count") or media.get("video_view_count") or 1
                
                # Date check - convert unix timestamp
                if taken_at > 0:
                    post_date = datetime.fromtimestamp(taken_at, tz=timezone.utc)
                    # Only filter if we have a valid date
                    if post_date < date_threshold:
                        continue
                    upload_date_str = post_date.strftime("%Y-%m-%d")
                else:
                    # If no date, include anyway
                    post_date = datetime.now(tz=timezone.utc)
                    upload_date_str = "unknown"
                
                # Build URL
                url = f"https://www.instagram.com/reel/{code}/"
                
                # Calculate engagement rate
                engagement_rate = ((likes + comments) / views * 100) if views > 0 else 0
                
                # Flag viral content
                viral = engagement_rate > 5 or views > 100000
                
                reel_data = {
                    'platform': 'instagram',
                    'source': 'rapidapi',
                    'title': caption[:100] if caption else 'No caption',
                    'caption': caption,
                    'views': views,
                    'likes': likes,
                    'comments': comments,
                    'url': url,
                    'upload_date': upload_date_str,
                    'engagement_rate': round(engagement_rate, 2),
                    'viral': viral,
                    'username': username
                }
                
                reels_data.append(reel_data)
                reel_count += 1
                
            except Exception as e:
                # Silently skip failed reels
                continue
        
        print(f"      ✅ Collected {reel_count} reels")
        return reels_data
        
    except requests.exceptions.Timeout:
        print(f"      ❌ Request timeout")
        return reels_data
    except Exception as e:
        print(f"      ❌ Error: {str(e)[:50]}")
        return reels_data


def scrape_instagram_rapidapi(iguser_file='iguser.txt'):
    """
    Scrape Instagram Reels using RapidAPI (2-step process)
    STEP 1: Get user_id from username
    STEP 2: Get reels from user_id
    
    Args:
        iguser_file: Path to file containing Instagram usernames
    
    Returns:
        Tuple: (list of post dicts, stats dict)
    """
    instagram_data = []
    stats = {
        'total_profiles': 0,
        'successful_profiles': 0,
        'failed_profiles': 0,
        'total_posts': 0,
        'api_requests': 0
    }
    
    # Check for RapidAPI key
    rapidapi_key = os.getenv('RAPIDAPI_KEY')
    
    if not rapidapi_key:
        print("\n" + "="*60)
        print("❌ RAPIDAPI_KEY NOT FOUND")
        print("="*60)
        print("Add RAPIDAPI_KEY to your .env file to enable Instagram scraping.")
        print("\nExample:")
        print("RAPIDAPI_KEY=your_rapidapi_key_here")
        print("="*60 + "\n")
        return instagram_data, stats
    
    try:
        # Read competitor handles
        if not os.path.exists(iguser_file):
            print(f"⚠️  Instagram user file not found: {iguser_file}")
            return instagram_data, stats
        
        with open(iguser_file, 'r', encoding='utf-8') as f:
            usernames = [line.strip().replace('@', '') for line in f if line.strip()]
        
        if not usernames:
            print("⚠️  No usernames found in iguser.txt")
            return instagram_data, stats
        
        stats['total_profiles'] = len(usernames)
        
        print(f"📸 Scraping {len(usernames)} Instagram profiles via RapidAPI...")
        print(f"   (2-step process: user_id lookup → reels)")
        print(f"   (Max 5 reels per profile, last 30 days)\n")
        
        for idx, username in enumerate(usernames, 1):
            print(f"   [{idx}/{len(usernames)}] @{username}")
            
            try:
                # STEP 1: Get user_id from username
                print(f"      🔍 Step 1: Looking up user_id...")
                user_id = get_user_id_from_username(username, rapidapi_key)
                stats['api_requests'] += 1
                
                if not user_id:
                    print(f"      ❌ Failed to get user_id\n")
                    stats['failed_profiles'] += 1
                    continue
                
                # STEP 2: Get reels from user_id
                print(f"      📥 Step 2: Fetching reels...")
                reels = get_reels_from_user_id(user_id, username, rapidapi_key)
                stats['api_requests'] += 1
                
                if reels:
                    instagram_data.extend(reels)
                    stats['total_posts'] += len(reels)
                    stats['successful_profiles'] += 1
                    print(f"      ✅ Success: {len(reels)} reels added\n")
                else:
                    stats['failed_profiles'] += 1
                    print(f"      ⚠️  No reels collected\n")
                
                # Sleep 1 second between profiles to avoid rate limiting
                if idx < len(usernames):
                    time.sleep(1)
                
                # Clear memory periodically
                if idx % 3 == 0:
                    import gc
                    gc.collect()
                        
            except Exception as e:
                print(f"      ❌ Profile failed: {str(e)[:50]}\n")
                stats['failed_profiles'] += 1
                continue
                
    except Exception as e:
        print(f"❌ Instagram scraping failed: {str(e)}")
    
    return instagram_data, stats


def scrape_twitter_search(rapidapi_key):
    """
    Scrape Twitter/X by keyword search using twitter-api45
    
    Args:
        rapidapi_key: RapidAPI key
    
    Returns:
        Tuple: (list of tweet dicts, api_requests count)
    """
    twitter_data = []
    api_requests = 0
    
    try:
        url = "https://twitter-api45.p.rapidapi.com/search.php"
        
        headers = {
            "x-rapidapi-key": rapidapi_key,
            "x-rapidapi-host": "twitter-api45.p.rapidapi.com"
        }
        
        print(f"🐦 Searching Twitter by keywords...")
        print(f"   (Top 5 tweets per query, last 30 days)\n")
        
        for idx, query in enumerate(TWITTER_SEARCH_QUERIES, 1):
            try:
                params = {
                    "query": query,
                    "search_type": "Top"
                }
                
                response = requests.get(url, headers=headers, params=params, timeout=10)
                api_requests += 1
                
                if response.status_code == 429:
                    print(f"   ⚠️  Rate limit reached")
                    break
                
                if response.status_code != 200:
                    print(f"   ❌ '{query}': API error ({response.status_code})")
                    time.sleep(0.5)
                    continue
                
                response_data = response.json()
                items = response_data.get("timeline", [])
                
                tweet_count = 0
                
                for item in items[:5]:
                    text = item.get("text", "")
                    if not text:
                        continue
                    
                    likes = int(item.get("favorites") or 0)
                    bookmarks = int(item.get("bookmarks") or 0)
                    views_str = item.get("views") or "0"
                    
                    try:
                        views = int(views_str)
                    except:
                        views = max(likes * 100, 1000)
                    
                    tweet_id = str(item.get("tweet_id", ""))
                    screen_name = item.get("screen_name", "unknown")
                    created_at = item.get("created_at", "")
                    
                    url_tweet = f"https://twitter.com/i/web/status/{tweet_id}"
                    er = round((likes + bookmarks) / views * 100, 2) if views > 0 else 0
                    viral = likes > 100 or views > 5000
                    
                    twitter_data.append({
                        "platform": "twitter",
                        "source": "search",
                        "title": text[:100],
                        "caption": text,
                        "views": views,
                        "likes": likes,
                        "comments": bookmarks,
                        "url": url_tweet,
                        "upload_date": created_at[:10] if created_at else "unknown",
                        "engagement_rate": er,
                        "viral": viral,
                        "username": screen_name,
                        "keyword": query
                    })
                    
                    tweet_count += 1
                
                print(f"   ✅ '{query}': {tweet_count} tweets")
                
                # Shorter delay and memory cleanup
                time.sleep(0.5)
                
                # Clear memory every 2 queries
                if idx % 2 == 0:
                    import gc
                    gc.collect()
                
            except Exception as e:
                print(f"   ❌ '{query}': Failed ({str(e)[:50]})")
                time.sleep(0.5)
                continue
        
    except Exception as e:
        print(f"❌ Twitter search failed: {str(e)}")
    
    return twitter_data, api_requests


def scrape_twitter_users(rapidapi_key, twitter_handles_file='twitter_handles.txt'):
    """
    Scrape Twitter/X by user timeline using twitter-api45
    
    Args:
        rapidapi_key: RapidAPI key
        twitter_handles_file: Path to file with Twitter handles
    
    Returns:
        Tuple: (list of tweet dicts, api_requests count)
    """
    twitter_data = []
    api_requests = 0
    
    try:
        # Read Twitter handles
        if not os.path.exists(twitter_handles_file):
            print(f"⚠️  Twitter handles file not found: {twitter_handles_file}")
            return twitter_data, api_requests
        
        with open(twitter_handles_file, 'r', encoding='utf-8') as f:
            handles = [line.strip().replace('@', '') for line in f if line.strip()]
        
        if not handles:
            return twitter_data, api_requests
        
        print(f"\n🐦 Scraping {len(handles)} Twitter accounts...")
        
        url = "https://twitter-api45.p.rapidapi.com/timeline.php"
        
        headers = {
            "x-rapidapi-key": rapidapi_key,
            "x-rapidapi-host": "twitter-api45.p.rapidapi.com"
        }
        
        for handle in handles:
            try:
                params = {"screenname": handle}
                
                response = requests.get(url, headers=headers, params=params, timeout=15)
                api_requests += 1
                
                if response.status_code == 429:
                    print(f"   ⚠️  Rate limit reached")
                    break
                
                if response.status_code != 200:
                    print(f"   ❌ @{handle}: API error ({response.status_code})")
                    time.sleep(1)
                    continue
                
                response_data = response.json()
                
                # Get pinned tweet first
                items = []
                pinned = response_data.get("pinned")
                if pinned and isinstance(pinned, dict):
                    items.append(pinned)
                
                # Add timeline tweets
                items += response_data.get("timeline", [])
                
                tweet_count = 0
                
                for item in items[:5]:
                    text = item.get("text", "")
                    if not text:
                        continue
                    
                    likes = int(item.get("favorites") or 0)
                    bookmarks = int(item.get("bookmarks") or 0)
                    views_str = item.get("views") or "0"
                    
                    try:
                        views = int(views_str)
                    except:
                        views = max(likes * 100, 1000)
                    
                    tweet_id = str(item.get("tweet_id", ""))
                    created_at = item.get("created_at", "")
                    
                    url_tweet = f"https://twitter.com/i/web/status/{tweet_id}"
                    er = round((likes + bookmarks) / views * 100, 2) if views > 0 else 0
                    viral = likes > 100 or views > 5000
                    
                    twitter_data.append({
                        "platform": "twitter",
                        "source": "user",
                        "title": text[:100],
                        "caption": text,
                        "views": views,
                        "likes": likes,
                        "comments": bookmarks,
                        "url": url_tweet,
                        "upload_date": created_at[:10] if created_at else "unknown",
                        "engagement_rate": er,
                        "viral": viral,
                        "username": handle
                    })
                    
                    tweet_count += 1
                
                print(f"   ✅ @{handle}: {tweet_count} tweets")
                
                # Shorter delay and memory cleanup
                time.sleep(0.5)
                
                # Clear memory periodically
                import gc
                gc.collect()
                
            except Exception as e:
                print(f"   ❌ @{handle}: Failed ({str(e)[:50]})")
                time.sleep(1)
                continue
        
    except Exception as e:
        print(f"❌ Twitter user scraping failed: {str(e)}")
    
    return twitter_data, api_requests


def scrape_twitter_all(rapidapi_key):
    """
    Scrape Twitter/X using both search and user methods
    
    Args:
        rapidapi_key: RapidAPI key
    
    Returns:
        Tuple: (list of tweet dicts, stats dict)
    """
    twitter_data = []
    stats = {
        'total_tweets': 0,
        'search_tweets': 0,
        'user_tweets': 0,
        'api_requests': 0
    }
    
    if not rapidapi_key:
        return twitter_data, stats
    
    try:
        # Method 1: Search by keywords
        search_results, search_requests = scrape_twitter_search(rapidapi_key)
        twitter_data.extend(search_results)
        stats['search_tweets'] = len(search_results)
        stats['api_requests'] += search_requests
        
        # Method 2: Tweets by username (only if under 15 total requests)
        if stats['api_requests'] < 15:
            user_results, user_requests = scrape_twitter_users(rapidapi_key)
            twitter_data.extend(user_results)
            stats['user_tweets'] = len(user_results)
            stats['api_requests'] += user_requests
        else:
            print("\n⚠️  Skipping user tweets to stay within API limits")
        
        stats['total_tweets'] = len(twitter_data)
        
    except Exception as e:
        print(f"❌ Twitter scraping failed: {str(e)}")
    
    return twitter_data, stats


def scrape_youtube_shorts(keywords):
    """
    BACKUP SCRAPER: YouTube Shorts with browser cookies
    Uses cookiesfrombrowser to avoid bot detection
    Priority: brave > chrome > firefox
    
    Args:
        keywords: List of keywords to search
    
    Returns:
        List of dicts with video data
    """
    youtube_data = []
    
    # Check if yt_dlp is available
    if not YT_DLP_AVAILABLE:
        print("📺 YouTube scraping unavailable (yt-dlp not installed)")
        return youtube_data
    
    # Check if running on Render (no browser available)
    if is_render_deployment():
        print("📺 Running on Render — YouTube skipped (no browser available)")
        return youtube_data
    
    # Try browsers in priority order
    browsers = ['brave', 'chrome', 'firefox']
    working_browser = None
    
    print("📺 Attempting YouTube scraping with browser cookies...")
    
    for browser in browsers:
        try:
            print(f"   Trying {browser}...")
            
            # Test if browser cookies work
            test_opts = {
                'quiet': True,
                'no_warnings': True,
                'cookiesfrombrowser': (browser,),
                'extract_flat': True,
                'skip_download': True,
            }
            
            with yt_dlp.YoutubeDL(test_opts) as ydl:
                # Quick test
                ydl.extract_info("ytsearch1:test", download=False)
                working_browser = browser
                print(f"   ✅ {browser} cookies loaded successfully\n")
                break
                
        except Exception as e:
            print(f"   ❌ {browser} failed")
            continue
    
    if not working_browser:
        print("\n" + "="*60)
        print("❌ YouTube scraping unavailable")
        print("="*60)
        print("Open Brave and visit youtube.com while logged in, then run again.")
        print("="*60 + "\n")
        return youtube_data
    
    try:
        # Configure yt-dlp with working browser cookies
        ydl_opts_flat = {
            'quiet': True,
            'no_warnings': True,
            'cookiesfrombrowser': (working_browser,),
            'extract_flat': True,
            'skip_download': True,
        }
        
        ydl_opts_detailed = {
            'quiet': True,
            'no_warnings': True,
            'cookiesfrombrowser': (working_browser,),
            'extract_flat': False,
            'skip_download': True,
        }
        
        print(f"📺 Scraping YouTube Shorts (using {working_browser} cookies)...\n")
        
        with yt_dlp.YoutubeDL(ydl_opts_flat) as ydl_flat:
            for keyword in keywords:
                try:
                    # Search for Shorts
                    search_query = f"ytsearch10:{keyword} shorts"
                    result = ydl_flat.extract_info(search_query, download=False)
                    
                    if not result or 'entries' not in result:
                        continue
                    
                    # Collect video IDs (top 5 per keyword)
                    video_ids = []
                    for entry in result['entries'][:5]:
                        if entry and entry.get('id'):
                            video_ids.append(entry['id'])
                    
                    # Fetch detailed info
                    with yt_dlp.YoutubeDL(ydl_opts_detailed) as ydl_detailed:
                        for video_id in video_ids:
                            try:
                                video_url = f"https://www.youtube.com/watch?v={video_id}"
                                video_info = ydl_detailed.extract_info(video_url, download=False)
                                
                                # Extract data
                                views = video_info.get('view_count', 0) or 0
                                likes = video_info.get('like_count', 0) or 0
                                upload_date_str = video_info.get('upload_date', '')
                                
                                # Parse upload date
                                if upload_date_str:
                                    upload_date = datetime.strptime(upload_date_str, '%Y%m%d')
                                else:
                                    upload_date = datetime.now()
                                
                                # Only include videos from last 7 days
                                if datetime.now() - upload_date > timedelta(days=7):
                                    continue
                                
                                # Calculate engagement rate
                                engagement_rate = (likes / views * 100) if views > 0 else 0
                                
                                # Flag viral content
                                viral = engagement_rate > 5 or views > 100000
                                
                                video_data = {
                                    'platform': 'youtube',
                                    'source': 'search',
                                    'title': video_info.get('title', 'No title'),
                                    'views': views,
                                    'likes': likes,
                                    'comments': 0,
                                    'url': video_url,
                                    'upload_date': upload_date.strftime('%Y-%m-%d'),
                                    'description': video_info.get('description', '')[:200],
                                    'engagement_rate': round(engagement_rate, 2),
                                    'viral': viral,
                                    'keyword': keyword
                                }
                                
                                youtube_data.append(video_data)
                                
                            except Exception as e:
                                continue
                                
                except Exception as e:
                    continue
        
        print(f"  ✅ YouTube: {len(youtube_data)} videos\n")
                    
    except Exception as e:
        print(f"❌ YouTube scraping failed: {str(e)}")
    
    return youtube_data


def run_scraper(keywords=None):
    """
    Main scraper function
    PRIMARY: Instagram via RapidAPI (2-step process)
    SECONDARY: Twitter/X via RapidAPI (search + users)
    BACKUP: YouTube (only if Instagram + Twitter < 10 posts, and not on Render)
    
    Args:
        keywords: List of keywords for YouTube search (backup only)
    
    Returns:
        Combined list with Instagram first, Twitter second, YouTube third
    """
    return run_scraper_selective(['instagram', 'twitter', 'youtube'], keywords)


def run_scraper_selective(platforms, keywords=None):
    """
    Selective scraper function - scrapes only from specified platforms
    
    Args:
        platforms: List of platforms to scrape ['instagram', 'twitter', 'youtube']
        keywords: List of keywords for YouTube search
    
    Returns:
        Combined list of posts from selected platforms
    """
    global scraped_data
    scraped_data = []
    
    # Default keywords for YouTube
    if not keywords:
        keywords = [
            'web development India 2025',
            'app development for business',
            'AI automation for entrepreneurs',
            'tech consulting India',
            'how to build a website business'
        ]
    
    # Check deployment environment
    on_render = is_render_deployment()
    
    # Get RapidAPI key
    rapidapi_key = os.getenv('RAPIDAPI_KEY')
    
    print("\n" + "="*60)
    print("🔍 SELECTIVE CONTENT SCRAPING")
    print("="*60)
    print(f"Selected platforms: {', '.join(platforms).upper()}")
    print("="*60 + "\n")
    
    instagram_count = 0
    twitter_count = 0
    youtube_count = 0
    
    ig_stats = {}
    twitter_stats = {}
    
    # INSTAGRAM
    if 'instagram' in platforms:
        print("📸 SCRAPING: Instagram via RapidAPI")
        print("-" * 60)
        instagram_results, ig_stats = scrape_instagram_rapidapi()
        scraped_data.extend(instagram_results)
        instagram_count = len(instagram_results)
        ig_viral_count = sum(1 for p in instagram_results if p.get('viral', False))
        
        print("\n" + "="*60)
        print("📊 INSTAGRAM SUMMARY")
        print("="*60)
        print(f"Total profiles: {ig_stats.get('total_profiles', 0)}")
        print(f"Successful: {ig_stats.get('successful_profiles', 0)}")
        print(f"Failed: {ig_stats.get('failed_profiles', 0)}")
        print(f"Total posts collected: {ig_stats.get('total_posts', 0)}")
        print(f"Viral posts: {ig_viral_count}")
        print(f"API requests used: {ig_stats.get('api_requests', 0)}")
        print("="*60 + "\n")
    
    # TWITTER
    if 'twitter' in platforms and rapidapi_key:
        print("🐦 SCRAPING: Twitter/X via RapidAPI")
        print("-" * 60)
        twitter_results, twitter_stats = scrape_twitter_all(rapidapi_key)
        scraped_data.extend(twitter_results)
        twitter_count = len(twitter_results)
        twitter_viral_count = sum(1 for p in twitter_results if p.get('viral', False))
        
        print("\n" + "="*60)
        print("📊 TWITTER SUMMARY")
        print("="*60)
        print(f"Search tweets: {twitter_stats.get('search_tweets', 0)}")
        print(f"User tweets: {twitter_stats.get('user_tweets', 0)}")
        print(f"Total tweets collected: {twitter_stats.get('total_tweets', 0)}")
        print(f"Viral tweets: {twitter_viral_count}")
        print(f"API requests used: {twitter_stats.get('api_requests', 0)}")
        print("="*60 + "\n")
    elif 'twitter' in platforms and not rapidapi_key:
        print("⚠️  RAPIDAPI_KEY not found - skipping Twitter\n")
    
    # YOUTUBE
    if 'youtube' in platforms:
        if on_render:
            print("="*60)
            print("Running on Render — YouTube skipped (no browser available).")
            print("="*60 + "\n")
        else:
            print("📺 SCRAPING: YouTube Shorts")
            print("-" * 60)
            youtube_results = scrape_youtube_shorts(keywords)
            scraped_data.extend(youtube_results)
            youtube_count = len(youtube_results)
            
            yt_viral = sum(1 for p in youtube_results if p.get('viral', False))
            
            print("\n" + "="*60)
            print("📊 YOUTUBE SUMMARY")
            print("="*60)
            print(f"Total videos collected: {youtube_count}")
            print(f"Viral videos: {yt_viral}")
            print("="*60 + "\n")
    
    # Final summary
    print("="*60)
    print("🎉 FINAL SUMMARY")
    print("="*60)
    print(f"Selected platforms: {', '.join(platforms)}")
    print(f"Total posts: {len(scraped_data)}")
    print(f"  📸 Instagram: {instagram_count} posts")
    print(f"  🐦 Twitter: {twitter_count} posts")
    print(f"  📺 YouTube: {youtube_count} posts")
    print(f"Viral posts: {sum(1 for p in scraped_data if p.get('viral', False))}")
    total_api_requests = ig_stats.get('api_requests', 0) + twitter_stats.get('api_requests', 0)
    print(f"Total API requests: {total_api_requests}")
    print("="*60 + "\n")
    
    return scraped_data


# For testing
import sys

if __name__ == '__main__':
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == "instagram" or mode == "ig":
            print("🧪 TESTING INSTAGRAM ONLY\n")
            results, stats = scrape_instagram_rapidapi()
            print(f"\n✅ Result: {len(results)} posts collected")
            if results:
                print("\nSample posts:")
                for i, p in enumerate(results[:3], 1):
                    print(f"\n{i}. {p['title'][:60]}")
                    print(f"   Views: {p['views']:,} | ER: {p['engagement_rate']}%")
                    print(f"   URL: {p['url']}")
        
        elif mode == "twitter" or mode == "tw":
            print("🧪 TESTING TWITTER ONLY\n")
            rapidapi_key = os.getenv('RAPIDAPI_KEY')
            if not rapidapi_key:
                print("❌ RAPIDAPI_KEY not found in .env")
            else:
                results, stats = scrape_twitter_all(rapidapi_key)
                print(f"\n✅ Result: {len(results)} tweets collected")
                if results:
                    print("\nSample tweets:")
                    for i, p in enumerate(results[:3], 1):
                        print(f"\n{i}. {p['title'][:60]}")
                        print(f"   Likes: {p['likes']} | Views: {p['views']:,}")
                        print(f"   URL: {p['url']}")
        
        elif mode == "youtube" or mode == "yt":
            print("🧪 TESTING YOUTUBE ONLY\n")
            keywords = [
                'web development India 2025',
                'AI automation for entrepreneurs'
            ]
            results = scrape_youtube_shorts(keywords)
            print(f"\n✅ Result: {len(results)} videos collected")
            if results:
                print("\nSample videos:")
                for i, p in enumerate(results[:3], 1):
                    print(f"\n{i}. {p['title'][:60]}")
                    print(f"   Views: {p['views']:,} | ER: {p['engagement_rate']}%")
                    print(f"   URL: {p['url']}")
        
        elif mode == "all":
            print("🧪 RUNNING FULL PIPELINE\n")
            run_scraper()
        
        else:
            print("❌ Unknown mode. Usage:")
            print("  python content_scraper.py ig        # Test Instagram only")
            print("  python content_scraper.py tw        # Test Twitter only")
            print("  python content_scraper.py yt        # Test YouTube only")
            print("  python content_scraper.py all       # Run full pipeline")
    
    else:
        # Default - show usage instead of running everything
        print("Usage:")
        print("  python content_scraper.py ig        # Test Instagram only")
        print("  python content_scraper.py tw        # Test Twitter only")
        print("  python content_scraper.py yt        # Test YouTube only")
        print("  python content_scraper.py all       # Run full pipeline")
