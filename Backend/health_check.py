"""
Health Check Views

This module contains health check endpoints for monitoring
the application status and dependencies.
"""

from django.http import JsonResponse
from django.views import View
from django.db import connection
from django.core.cache import cache
from django.conf import settings
import redis
import psutil
import time
from datetime import datetime


class HealthCheckView(View):
    """
    Comprehensive health check endpoint that verifies:
    - Database connectivity
    - Redis connectivity
    - Application status
    - System resources
    """
    
    def get(self, request):
        """Perform health check and return status"""
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'checks': {}
        }
        
        # Check database connectivity
        db_status = self._check_database()
        health_status['checks']['database'] = db_status
        
        # Check Redis connectivity
        redis_status = self._check_redis()
        health_status['checks']['redis'] = redis_status
        
        # Check system resources
        system_status = self._check_system_resources()
        health_status['checks']['system'] = system_status
        
        # Check application status
        app_status = self._check_application()
        health_status['checks']['application'] = app_status
        
        # Determine overall status
        all_healthy = all(
            check.get('status') == 'healthy' 
            for check in health_status['checks'].values()
        )
        
        if not all_healthy:
            health_status['status'] = 'unhealthy'
            return JsonResponse(health_status, status=503)
        
        return JsonResponse(health_status, status=200)
    
    def _check_database(self):
        """Check database connectivity and performance"""
        try:
            start_time = time.time()
            
            # Test database connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            return {
                'status': 'healthy',
                'response_time_ms': round(response_time, 2),
                'database': settings.DATABASES['default']['ENGINE'].split('.')[-1]
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'database': settings.DATABASES['default']['ENGINE'].split('.')[-1]
            }
    
    def _check_redis(self):
        """Check Redis connectivity and performance"""
        try:
            start_time = time.time()
            
            # Test Redis connection
            cache.set('health_check', 'test', 10)
            value = cache.get('health_check')
            cache.delete('health_check')
            
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            if value == 'test':
                return {
                    'status': 'healthy',
                    'response_time_ms': round(response_time, 2),
                    'backend': 'redis'
                }
            else:
                return {
                    'status': 'unhealthy',
                    'error': 'Cache test failed',
                    'backend': 'redis'
                }
                
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'backend': 'redis'
            }
    
    def _check_system_resources(self):
        """Check system resource usage"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # Determine status based on thresholds
            status = 'healthy'
            warnings = []
            
            if cpu_percent > 80:
                status = 'warning'
                warnings.append(f'High CPU usage: {cpu_percent}%')
            
            if memory_percent > 85:
                status = 'warning'
                warnings.append(f'High memory usage: {memory_percent}%')
            
            if disk_percent > 90:
                status = 'warning'
                warnings.append(f'High disk usage: {disk_percent}%')
            
            return {
                'status': status,
                'cpu_percent': round(cpu_percent, 2),
                'memory_percent': round(memory_percent, 2),
                'disk_percent': round(disk_percent, 2),
                'warnings': warnings
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    def _check_application(self):
        """Check application-specific health"""
        try:
            # Check if all required apps are installed
            required_apps = ['accounts', 'products', 'orders', 'search']
            installed_apps = settings.INSTALLED_APPS
            
            missing_apps = [app for app in required_apps if app not in installed_apps]
            
            if missing_apps:
                return {
                    'status': 'unhealthy',
                    'error': f'Missing required apps: {missing_apps}'
                }
            
            # Check if debug mode is disabled in production
            if not settings.DEBUG:
                return {
                    'status': 'healthy',
                    'debug_mode': False,
                    'environment': 'production'
                }
            else:
                return {
                    'status': 'warning',
                    'debug_mode': True,
                    'environment': 'development',
                    'warning': 'Debug mode is enabled'
                }
                
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }


class ReadinessCheckView(View):
    """
    Readiness check endpoint for Kubernetes/Docker health checks.
    This is a lighter check that only verifies critical dependencies.
    """
    
    def get(self, request):
        """Perform readiness check"""
        try:
            # Check database
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            
            # Check Redis
            cache.set('readiness_check', 'test', 5)
            cache.get('readiness_check')
            cache.delete('readiness_check')
            
            return JsonResponse({
                'status': 'ready',
                'timestamp': datetime.now().isoformat()
            }, status=200)
            
        except Exception as e:
            return JsonResponse({
                'status': 'not_ready',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }, status=503)


class LivenessCheckView(View):
    """
    Liveness check endpoint for Kubernetes/Docker health checks.
    This is the lightest check that only verifies the application is running.
    """
    
    def get(self, request):
        """Perform liveness check"""
        return JsonResponse({
            'status': 'alive',
            'timestamp': datetime.now().isoformat()
        }, status=200)
