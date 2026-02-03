"""
Custom middleware for production features
"""
import time
import logging
from typing import Dict, Any
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import asyncio
from collections import defaultdict, deque
from datetime import datetime, timedelta

from ..config import get_settings
from ..utils.exceptions import RateLimitError

logger = logging.getLogger(__name__)
settings = get_settings()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware"""
    
    def __init__(self, app):
        super().__init__(app)
        self.requests = defaultdict(deque)
        self.rate_limit = settings.rate_limit_per_minute
        self.window_size = 60  # 1 minute
    
    async def dispatch(self, request: Request, call_next):
        client_ip = self._get_client_ip(request)
        current_time = datetime.now()
        
        # Clean old requests
        self._clean_old_requests(client_ip, current_time)
        
        # Check rate limit
        if len(self.requests[client_ip]) >= self.rate_limit:
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "message": "Rate limit exceeded",
                    "retry_after": 60
                }
            )
        
        # Add current request
        self.requests[client_ip].append(current_time)
        
        response = await call_next(request)
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host
    
    def _clean_old_requests(self, client_ip: str, current_time: datetime):
        """Remove requests older than window size"""
        cutoff_time = current_time - timedelta(seconds=self.window_size)
        
        while (self.requests[client_ip] and 
               self.requests[client_ip][0] < cutoff_time):
            self.requests[client_ip].popleft()


class LoggingMiddleware(BaseHTTPMiddleware):
    """Request/response logging middleware"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url}")
        
        response = await call_next(request)
        
        # Log response
        process_time = time.time() - start_time
        logger.info(
            f"Response: {response.status_code} - "
            f"Time: {process_time:.3f}s - "
            f"Path: {request.url.path}"
        )
        
        # Add timing header
        response.headers["X-Process-Time"] = str(process_time)
        
        return response


class SecurityMiddleware(BaseHTTPMiddleware):
    """Security headers middleware"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        if not settings.debug:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response


class MetricsMiddleware(BaseHTTPMiddleware):
    """Metrics collection middleware"""
    
    def __init__(self, app):
        super().__init__(app)
        self.metrics = {
            "requests_total": 0,
            "requests_by_endpoint": defaultdict(int),
            "response_times": deque(maxlen=1000),
            "error_count": 0,
            "success_count": 0
        }
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Increment request counter
        self.metrics["requests_total"] += 1
        self.metrics["requests_by_endpoint"][request.url.path] += 1
        
        response = await call_next(request)
        
        # Record response time
        response_time = time.time() - start_time
        self.metrics["response_times"].append(response_time)
        
        # Record success/error
        if response.status_code >= 400:
            self.metrics["error_count"] += 1
        else:
            self.metrics["success_count"] += 1
        
        return response
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        response_times = list(self.metrics["response_times"])
        
        return {
            "requests_total": self.metrics["requests_total"],
            "success_count": self.metrics["success_count"],
            "error_count": self.metrics["error_count"],
            "success_rate": (
                self.metrics["success_count"] / max(self.metrics["requests_total"], 1)
            ),
            "average_response_time": (
                sum(response_times) / len(response_times) if response_times else 0
            ),
            "requests_by_endpoint": dict(self.metrics["requests_by_endpoint"])
        }


# Global metrics instance
metrics_middleware = None


def get_metrics() -> Dict[str, Any]:
    """Get application metrics"""
    if metrics_middleware:
        return metrics_middleware.get_metrics()
    return {"error": "Metrics not available"}