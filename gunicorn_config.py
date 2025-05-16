import multiprocessing
import os

# Gunicorn configuration file for production deployment

# Bind to 0.0.0.0:PORT (PORT from environment variable or default to 8000)
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"

# Worker configuration
# Use 2-4 workers per CPU core for CPU-bound applications
# Use 2-4 workers per CPU core * 2 for IO-bound applications
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'gevent'  # Use gevent for async workers
worker_connections = 1000

# Timeout configuration
timeout = 120  # 2 minutes
keepalive = 5

# Logging
accesslog = '-'  # Log to stdout
errorlog = '-'   # Log to stderr
loglevel = 'info'

# Security
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

# Server mechanics
daemon = False
reload = False  # Set to True for development
preload_app = True

# Debugging
check_config = True
