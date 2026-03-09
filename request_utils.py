import asyncio
import random
import time
from collections import deque

from aiohttp import ClientResponseError

from http_client import get_session

MAX_RETRIES = 5


class RollingRateLimiter:
    def __init__(self, max_requests: int, per_seconds: int):
        self.max_requests = max_requests
        self.per_seconds = per_seconds
        self.timestamps = deque()
        self._lock = asyncio.Lock()

    async def wait(self):
        async with self._lock:
            now = time.monotonic()

            while self.timestamps and now - self.timestamps[0] > self.per_seconds:
                self.timestamps.popleft()

            if len(self.timestamps) >= self.max_requests:
                sleep_time = self.per_seconds - (now - self.timestamps[0])
                await asyncio.sleep(sleep_time + random.uniform(0.05, 0.25))

            self.timestamps.append(time.monotonic())


limiter = RollingRateLimiter(
    max_requests=25,
    per_seconds=60,
)


async def rate_limited_get_json(url: str):

    session = await get_session()

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            await limiter.wait()

            async with session.get(url) as resp:
                if resp.status == 429:
                    raise ClientResponseError(
                        resp.request_info,
                        resp.history,
                        status=429,
                        message="Rate limited",
                    )

                resp.raise_for_status()

                return await resp.json()

        except ClientResponseError as e:
            if e.status == 429:
                wait_time = 2**attempt

                await asyncio.sleep(wait_time)

            else:
                raise

    raise Exception(f"Max retries exceeded for {url}")
