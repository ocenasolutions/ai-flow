"""
Gunicorn configuration for Render deployment
Optimized for memory-constrained environments
"""

import os
import multiprocessing

# Server socket
bind = f"0.0.0.0:{os.getenv('PORT', '5000')}"
backlog = 2048

# Worker processes
workers = 1  # Single worker to minimize memory usage
worker_class = 'gthread'
threads = 2  # 2 threads per worker
worker_connections = 100
max_requests = 100  # Restart worker after 100 requests to prevent memory leaks
max_requests_jitter = 10

# Timeouts
timeout = 300  # 5 minutes for long-running research operations
graceful_timeout = 30
keepalive = 2

# Memory management
worker_tmp_dir = '/dev/shm'  # Use shared memory for worker heartbeat

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = 'ai-content-flow'

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Preload app for memory efficiency
preload_app = False  # Set to False to avoid memory issues with forking

def on_starting(server):
    """Called just before the master process is initialized."""
    server.log.info("Starting AI Content Flow server...")

def on_reload(server):
    """Called to recycle workers during a reload via SIGHUP."""
    server.log.info("Reloading workers...")

def when_ready(server):
    """Called just after the server is started."""
    server.log.info("Server is ready. Spawning workers...")

def worker_int(worker):
    """Called when a worker receives the SIGINT or SIGQUIT signal."""
    worker.log.info("Worker received INT or QUIT signal")

def worker_abort(worker):
    """Called when a worker receives the SIGABRT signal."""
    worker.log.info("Worker received SIGABRT signal")
