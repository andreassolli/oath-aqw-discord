import aiohttp

_session: aiohttp.ClientSession | None = None


async def get_session() -> aiohttp.ClientSession:
    global _session

    if _session is None or _session.closed:
        timeout = aiohttp.ClientTimeout(total=10)
        _session = aiohttp.ClientSession(
            timeout=timeout,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "Accept": "text/html,application/xhtml+xml",
            },
        )

    return _session


async def close_session():
    global _session

    if _session and not _session.closed:
        await _session.close()
