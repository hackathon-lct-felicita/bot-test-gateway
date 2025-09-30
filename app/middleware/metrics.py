"""Middleware for collecting Prometheus metrics."""

import logging
import time
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.services.metrics_service import metrics_service

logger = logging.getLogger(__name__)


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware for collecting HTTP request metrics."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and collect metrics."""
        start_time = time.time()

        # Skip metrics collection for /metrics endpoint to avoid recursion
        if request.url.path == "/metrics":
            return await call_next(request)

        # Process the request
        response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time

        # Extract metrics
        method = request.method
        endpoint = self._get_endpoint_pattern(request.url.path)
        status_code = response.status_code

        # Record metrics
        try:
            metrics_service.record_http_request(
                method=method,
                endpoint=endpoint,
                status_code=status_code,
                duration=duration,
            )
        except Exception as e:
            logger.error(f"Failed to record HTTP metrics: {e}")

        return response

    def _get_endpoint_pattern(self, path: str) -> str:
        """Convert specific paths to patterns for better metric grouping."""
        # Convert specific IDs to patterns
        if path.startswith("/api/predict"):
            return "/api/predict"
        elif path.startswith("/api/"):
            return "/api/*"
        elif path == "/":
            return "/"
        elif path == "/health":
            return "/health"
        elif path == "/metrics":
            return "/metrics"
        else:
            return "other"
