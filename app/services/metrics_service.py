"""Prometheus metrics service for monitoring application performance."""

from typing import Any

from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    Info,
    generate_latest,
)


class MetricsService:
    """Service for collecting and exposing Prometheus metrics."""

    def __init__(self):
        """Initialize metrics collectors."""
        # HTTP request metrics
        self.http_requests_total = Counter(
            "http_requests_total",
            "Total number of HTTP requests",
            ["method", "endpoint", "status_code"],
        )

        self.http_request_duration_seconds = Histogram(
            "http_request_duration_seconds",
            "HTTP request duration in seconds",
            ["method", "endpoint"],
            buckets=(
                0.001,
                0.005,
                0.01,
                0.025,
                0.05,
                0.075,
                0.1,
                0.25,
                0.5,
                0.75,
                1.0,
                2.5,
                5.0,
                7.5,
                10.0,
            ),
        )

        # Prediction service metrics
        self.predict_requests_total = Counter(
            "predict_requests_total", "Total number of prediction requests", ["status"]
        )

        self.predict_duration_seconds = Histogram(
            "predict_duration_seconds",
            "Prediction request duration in seconds",
            buckets=(
                0.001,
                0.005,
                0.01,
                0.025,
                0.05,
                0.075,
                0.1,
                0.25,
                0.5,
                0.75,
                1.0,
                2.5,
                5.0,
                7.5,
                10.0,
            ),
        )

        # RPC metrics
        self.rpc_requests_total = Counter(
            "rpc_requests_total", "Total number of RPC requests", ["status"]
        )

        self.rpc_duration_seconds = Histogram(
            "rpc_duration_seconds",
            "RPC request duration in seconds",
            buckets=(
                0.001,
                0.005,
                0.01,
                0.025,
                0.05,
                0.075,
                0.1,
                0.25,
                0.5,
                0.75,
                1.0,
                2.5,
                5.0,
                7.5,
                10.0,
            ),
        )

        # System metrics
        self.active_connections = Gauge(
            "active_connections", "Number of active connections"
        )

        self.application_info = Info("application_info", "Application information")

        # Set application info
        self.application_info.info(
            {
                "name": "bot-test-gateway",
                "version": "0.1.0",
                "description": "High-performance service for entity prediction",
            }
        )

    def record_http_request(
        self, method: str, endpoint: str, status_code: int, duration: float
    ) -> None:
        """Record HTTP request metrics."""
        self.http_requests_total.labels(
            method=method, endpoint=endpoint, status_code=str(status_code)
        ).inc()

        self.http_request_duration_seconds.labels(
            method=method, endpoint=endpoint
        ).observe(duration)

    def record_predict_request(self, status: str, duration: float) -> None:
        """Record prediction request metrics."""
        self.predict_requests_total.labels(status=status).inc()
        self.predict_duration_seconds.observe(duration)

    def record_rpc_request(self, status: str, duration: float) -> None:
        """Record RPC request metrics."""
        self.rpc_requests_total.labels(status=status).inc()
        self.rpc_duration_seconds.observe(duration)

    def set_active_connections(self, count: int) -> None:
        """Set the number of active connections."""
        self.active_connections.set(count)

    def get_metrics(self) -> tuple[bytes, str]:
        """Get metrics in Prometheus format."""
        return generate_latest(), CONTENT_TYPE_LATEST

    def get_metrics_dict(self) -> dict[str, Any]:
        """Get metrics as dictionary for debugging."""
        return {
            "http_requests_total": self.http_requests_total._value.sum(),
            "predict_requests_total": self.predict_requests_total._value.sum(),
            "rpc_requests_total": self.rpc_requests_total._value.sum(),
            "active_connections": self.active_connections._value._value,
        }


# Global metrics service instance
metrics_service = MetricsService()
