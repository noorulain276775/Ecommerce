"""
Advanced monitoring and logging system for Django E-commerce
"""
import logging
import json
import time
from django.utils import timezone
from django.db import connection
from django.db import reset_queries
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth import get_user_model
from functools import wraps
import psutil
import os
from typing import Dict, Any, Optional

User = get_user_model()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/django.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Monitor API performance and database queries"""
    
    def __init__(self):
        self.start_time = None
        self.query_count = 0
        self.query_time = 0
    
    def start(self):
        """Start performance monitoring"""
        self.start_time = time.time()
        reset_queries()
    
    def stop(self):
        """Stop performance monitoring and log results"""
        if self.start_time:
            duration = time.time() - self.start_time
            queries = connection.queries
            query_count = len(queries)
            query_time = sum(float(q['time']) for q in queries)
            
            # Log performance metrics
            logger.info(f"Performance Metrics - Duration: {duration:.3f}s, "
                       f"Queries: {query_count}, Query Time: {query_time:.3f}s")
            
            # Alert on performance issues
            if query_count > 10:
                logger.warning(f"High query count detected: {query_count} queries")
            
            if duration > 2.0:
                logger.warning(f"Slow request detected: {duration:.3f}s")
            
            if query_time > 1.0:
                logger.warning(f"High database time detected: {query_time:.3f}s")
            
            return {
                'duration': duration,
                'query_count': query_count,
                'query_time': query_time,
                'queries': queries
            }

class LoggingMiddleware:
    """Middleware for comprehensive request/response logging"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Start performance monitoring
        monitor = PerformanceMonitor()
        monitor.start()
        
        # Log request
        self.log_request(request)
        
        # Process request
        response = self.get_response(request)
        
        # Stop monitoring and log response
        performance_data = monitor.stop()
        self.log_response(request, response, performance_data)
        
        return response
    
    def log_request(self, request):
        """Log incoming request details"""
        user = getattr(request.user, 'phone', 'anonymous') if hasattr(request, 'user') else 'anonymous'
        
        log_data = {
            'type': 'request',
            'method': request.method,
            'path': request.path,
            'user': user,
            'ip': self.get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'timestamp': timezone.now().isoformat(),
            'query_params': dict(request.GET),
            'content_type': request.content_type,
            'content_length': request.META.get('CONTENT_LENGTH', 0)
        }
        
        # Log request body for non-GET requests (excluding sensitive data)
        if request.method in ['POST', 'PUT', 'PATCH']:
            try:
                body = request.body.decode('utf-8')
                # Remove sensitive fields
                sensitive_fields = ['password', 'token', 'secret', 'key']
                if any(field in body.lower() for field in sensitive_fields):
                    log_data['body'] = '[SENSITIVE DATA FILTERED]'
                else:
                    log_data['body'] = body[:1000]  # Limit body size
            except:
                log_data['body'] = '[BINARY DATA]'
        
        logger.info(f"Request: {json.dumps(log_data)}")
    
    def log_response(self, request, response, performance_data):
        """Log response details and performance metrics"""
        user = getattr(request.user, 'phone', 'anonymous') if hasattr(request, 'user') else 'anonymous'
        
        log_data = {
            'type': 'response',
            'method': request.method,
            'path': request.path,
            'user': user,
            'status_code': response.status_code,
            'timestamp': timezone.now().isoformat(),
            'response_size': len(response.content) if hasattr(response, 'content') else 0,
            'performance': performance_data
        }
        
        # Log error details for 4xx and 5xx responses
        if response.status_code >= 400:
            log_data['error'] = True
            if hasattr(response, 'content'):
                try:
                    error_content = response.content.decode('utf-8')
                    log_data['error_content'] = error_content[:500]  # Limit error content
                except:
                    log_data['error_content'] = '[BINARY ERROR DATA]'
        
        logger.info(f"Response: {json.dumps(log_data)}")
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class SystemMonitor:
    """Monitor system resources and health"""
    
    @staticmethod
    def get_system_metrics():
        """Get current system metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # Database connections
            db_connections = len(connection.queries) if hasattr(connection, 'queries') else 0
            
            # Cache status
            cache_status = 'available' if cache else 'unavailable'
            
            return {
                'timestamp': timezone.now().isoformat(),
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'disk_percent': disk_percent,
                'db_connections': db_connections,
                'cache_status': cache_status,
                'process_count': len(psutil.pids())
            }
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return None
    
    @staticmethod
    def check_health():
        """Check overall system health"""
        metrics = SystemMonitor.get_system_metrics()
        if not metrics:
            return {'status': 'unhealthy', 'error': 'Unable to get system metrics'}
        
        health_status = 'healthy'
        warnings = []
        
        # Check CPU usage
        if metrics['cpu_percent'] > 80:
            health_status = 'warning'
            warnings.append(f"High CPU usage: {metrics['cpu_percent']}%")
        
        # Check memory usage
        if metrics['memory_percent'] > 85:
            health_status = 'warning'
            warnings.append(f"High memory usage: {metrics['memory_percent']}%")
        
        # Check disk usage
        if metrics['disk_percent'] > 90:
            health_status = 'critical'
            warnings.append(f"High disk usage: {metrics['disk_percent']}%")
        
        return {
            'status': health_status,
            'metrics': metrics,
            'warnings': warnings,
            'timestamp': timezone.now().isoformat()
        }

class APIMetrics:
    """Track API usage metrics"""
    
    @staticmethod
    def track_api_call(endpoint: str, method: str, user: Optional[User] = None, 
                      status_code: int = 200, duration: float = 0):
        """Track API call metrics"""
        try:
            metrics_key = f"api_metrics:{endpoint}:{method}"
            
            # Get current metrics
            metrics = cache.get(metrics_key, {
                'total_calls': 0,
                'successful_calls': 0,
                'failed_calls': 0,
                'total_duration': 0,
                'avg_duration': 0,
                'last_called': None,
                'unique_users': set()
            })
            
            # Update metrics
            metrics['total_calls'] += 1
            metrics['total_duration'] += duration
            
            if 200 <= status_code < 400:
                metrics['successful_calls'] += 1
            else:
                metrics['failed_calls'] += 1
            
            metrics['avg_duration'] = metrics['total_duration'] / metrics['total_calls']
            metrics['last_called'] = timezone.now().isoformat()
            
            if user:
                metrics['unique_users'].add(user.id)
            
            # Store updated metrics (cache for 1 hour)
            cache.set(metrics_key, metrics, 3600)
            
        except Exception as e:
            logger.error(f"Error tracking API metrics: {e}")
    
    @staticmethod
    def get_api_metrics(endpoint: str = None, method: str = None):
        """Get API metrics"""
        try:
            if endpoint and method:
                key = f"api_metrics:{endpoint}:{method}"
                return cache.get(key)
            else:
                # Get all API metrics
                pattern = "api_metrics:*"
                if hasattr(cache, 'keys'):
                    keys = cache.keys(pattern)
                    metrics = {}
                    for key in keys:
                        endpoint_method = key.replace('api_metrics:', '')
                        metrics[endpoint_method] = cache.get(key)
                    return metrics
                return {}
        except Exception as e:
            logger.error(f"Error getting API metrics: {e}")
            return {}

class ErrorTracker:
    """Track and analyze errors"""
    
    @staticmethod
    def track_error(error: Exception, request=None, user: Optional[User] = None):
        """Track error occurrence"""
        try:
            error_data = {
                'error_type': type(error).__name__,
                'error_message': str(error),
                'timestamp': timezone.now().isoformat(),
                'user': user.id if user else None,
                'path': request.path if request else None,
                'method': request.method if request else None,
                'ip': LoggingMiddleware(None).get_client_ip(request) if request else None
            }
            
            # Store error in cache for analysis
            error_key = f"error:{error_data['error_type']}:{int(time.time())}"
            cache.set(error_key, error_data, 86400)  # Store for 24 hours
            
            # Log error
            logger.error(f"Error tracked: {json.dumps(error_data)}")
            
        except Exception as e:
            logger.error(f"Error tracking error: {e}")
    
    @staticmethod
    def get_error_summary(hours: int = 24):
        """Get error summary for the last N hours"""
        try:
            # This would need to be implemented with a proper error storage system
            # For now, return a placeholder
            return {
                'total_errors': 0,
                'error_types': {},
                'most_common_errors': [],
                'time_range': f"Last {hours} hours"
            }
        except Exception as e:
            logger.error(f"Error getting error summary: {e}")
            return {}

# Decorators for monitoring
def monitor_performance(func):
    """Decorator to monitor function performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        monitor = PerformanceMonitor()
        monitor.start()
        
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            performance_data = monitor.stop()
            logger.info(f"Function {func.__name__} performance: {performance_data}")
    
    return wrapper

def track_api_usage(endpoint: str, method: str):
    """Decorator to track API usage"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            user = None
            
            # Try to get user from request
            if args and hasattr(args[0], 'user'):
                user = args[0].user
            
            try:
                result = func(*args, **kwargs)
                status_code = 200
                return result
            except Exception as e:
                status_code = 500
                ErrorTracker.track_error(e, args[0] if args else None, user)
                raise
            finally:
                duration = time.time() - start_time
                APIMetrics.track_api_call(endpoint, method, user, status_code, duration)
        
        return wrapper
    return decorator

# Health check endpoint data
def get_health_check_data():
    """Get comprehensive health check data"""
    return {
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'version': '1.0.0',
        'system': SystemMonitor.check_health(),
        'database': {
            'status': 'connected',
            'connection_count': len(connection.queries) if hasattr(connection, 'queries') else 0
        },
        'cache': {
            'status': 'available' if cache else 'unavailable',
            'backend': getattr(settings, 'CACHES', {}).get('default', {}).get('BACKEND', 'unknown')
        },
        'api_metrics': APIMetrics.get_api_metrics(),
        'error_summary': ErrorTracker.get_error_summary()
    }

# Logging configuration
def configure_logging():
    """Configure application logging"""
    log_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
                'style': '{',
            },
            'simple': {
                'format': '{levelname} {message}',
                'style': '{',
            },
            'json': {
                'format': '{"level": "%(levelname)s", "time": "%(asctime)s", "module": "%(module)s", "message": "%(message)s"}',
            },
        },
        'handlers': {
            'file': {
                'level': 'INFO',
                'class': 'logging.FileHandler',
                'filename': 'logs/django.log',
                'formatter': 'verbose',
            },
            'console': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'simple',
            },
            'error_file': {
                'level': 'ERROR',
                'class': 'logging.FileHandler',
                'filename': 'logs/errors.log',
                'formatter': 'json',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['file', 'console'],
                'level': 'INFO',
                'propagate': True,
            },
            'ecommerce': {
                'handlers': ['file', 'console', 'error_file'],
                'level': 'INFO',
                'propagate': True,
            },
        },
    }
    
    return log_config
