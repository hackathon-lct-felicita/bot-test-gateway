import socket
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class HeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add custom headers to responses."""

    def __init__(self, app):
        super().__init__(app)
        self.hostname = socket.gethostname()

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)

        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = f"{process_time:.6f}"
        response.headers["X-Hostname"] = self.hostname

        return response
