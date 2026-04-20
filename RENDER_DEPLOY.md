# Render Deployment Guide

## Quick Deploy

```bash
cd content-flow
git add .
git commit -m "Fix: Memory optimization for Render deployment"
git push origin main
```

Render will auto-deploy if connected to your GitHub repo.

## What Was Fixed

### Problem
- Worker timeout after ~10 minutes
- Out of Memory (OOM) errors
- Worker killed with SIGKILL

### Solution
1. **Gunicorn optimization** - Single worker, 2 threads, 5-min timeout
2. **Memory management** - Garbage collection after API calls
3. **Request timeout** - 4-minute max for /research endpoint
4. **Removed heavy deps** - yt-dlp and instaloader (not needed on Render)

## Configuration Files

- `Procfile` - Gunicorn startup command
- `gunicorn_config.py` - Worker and timeout settings
- `requirements.txt` - Minimal dependencies
- `runtime.txt` - Python 3.11.9

## Environment Variables (Set in Render Dashboard)

```
GROQ_API_KEY=your_groq_key_here
RAPIDAPI_KEY=your_rapidapi_key_here
```

Render auto-sets:
- `RENDER=true`
- `PORT=10000`

## Testing After Deploy

1. **Check logs** in Render dashboard
2. **Test health endpoint**: `https://your-app.onrender.com/health`
3. **Test research**: Use the web UI to run a research query

## Expected Behavior

- Research should complete in 2-5 minutes
- Memory usage: ~200-400MB (within 512MB free tier)
- No worker timeouts or SIGKILL errors

## If Issues Persist

### Check Memory Usage
Visit: `https://your-app.onrender.com/health`

Response shows current memory:
```json
{
  "status": "ok",
  "memory_mb": 234.56,
  "pid": 42
}
```

### Upgrade Plan
If still hitting OOM:
- Free tier: 512MB RAM
- **Starter tier: 2GB RAM** ← Recommended for production

### Further Optimizations
1. Reduce number of profiles in `iguser.txt` and `twitter_handles.txt`
2. Limit keywords to 3-5 instead of 10
3. Implement Redis caching for repeated queries
4. Use background job queue (Celery) for long operations

## Monitoring

Watch Render logs for:
- ✅ `Server is ready. Spawning workers...`
- ✅ `Research complete! Found X trending topics`
- ❌ `Worker (pid:X) was sent SIGKILL!` ← Bad
- ❌ `WORKER TIMEOUT` ← Bad

## Support

If deployment fails:
1. Check Render logs for specific errors
2. Verify environment variables are set
3. Test locally first: `python app.py`
4. Check GitHub repo is connected to Render
