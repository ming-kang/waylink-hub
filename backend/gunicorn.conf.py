"""
Gunicorn configuration for WaylinkHub.

Run with: gunicorn -c gunicorn.conf.py waylink.wsgi:application
"""

import os
import multiprocessing

# Directory - gunicorn.conf.py is in /backend/, so base_dir is /backend
base_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(base_dir)

# Workers
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 2

# Process naming
proc_name = 'waylink'

# Server socket
bind = os.environ.get('GUNICORN_BIND', '127.0.0.1:8000')
backlog = 2048

# Process management
pidfile = os.path.join(base_dir, 'logs/gunicorn.pid')
umask = 0
user = None
group = None
tmp_upload_dir = None

# Logging
errorlog = os.path.join(base_dir, 'logs/gunicorn-error.log')
accesslog = os.path.join(base_dir, 'logs/gunicorn-access.log')
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Preload app for memory efficiency with multiple workers
preload_app = True

def on_starting(server):
    """Called just before the master process is initialized."""
    pass

def on_reload(server):
    """Called to recycle workers during reload."""
    pass

def worker_int(worker):
    """Called when worker receives INT or QUIT signal."""
    pass

def worker_abort(worker):
    """Called when worker receives SIGABRT signal."""
    pass
