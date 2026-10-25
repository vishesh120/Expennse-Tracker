import time
from collections import defaultdict
from fastapi import Request, HTTPException, status


class SimpleRateLimiter:
    """
    In-memory sliding-window rate limiter for sensitive endpoints.
    Protects against brute force and automated request flooding.
    """
    def __init__(self, max_requests: int = 15, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.clients = defaultdict(list)

    def __call__(self, request: Request):
        client_ip = request.client.host if request.client else "127.0.0.1"
        now = time.time()
        window_start = now - self.window_seconds

        # Clean timestamps older than window
        timestamps = [t for t in self.clients[client_ip] if t > window_start]
        self.clients[client_ip] = timestamps

        # Periodic prune if client registry grows large (prevent memory leak)
        if len(self.clients) > 500:
            stale_ips = [ip for ip, ts in self.clients.items() if not ts or ts[-1] <= window_start]
            for ip in stale_ips:
                del self.clients[ip]

        if len(timestamps) >= self.max_requests:
            retry_after = int(self.window_seconds - (now - timestamps[0]))
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many authentication attempts. Please try again later.",
                headers={"Retry-After": str(max(1, retry_after))}
            )

        self.clients[client_ip].append(now)


auth_rate_limiter = SimpleRateLimiter(max_requests=20, window_seconds=60)
