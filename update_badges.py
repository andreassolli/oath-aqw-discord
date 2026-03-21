import asyncio
import logging
import random
import time
from collections import deque
from datetime import UTC, datetime
from urllib.parse import parse_qs, quote

import aiohttp
import discord
from aiohttp import ClientResponseError
from google.cloud.firestore_v1 import ArrayUnion, FieldFilter

from config import AQW_BADGES, CCID_PAGE
from firebase_client import db
from http_client import get_session
from user_verification.utils import AQWProfile

CONCURRENCY_LIMIT = 3

BATCH_SIZE = 400
MAX_RETRIES = 5
REQUESTS_PER_SECOND = 0.3

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1475789852078379018/YCRIfYbFbd256TAlMERpZxXjhDZg4xRc8RV5ejx7HlJo67KQY2PZhSp64ealO2EoQ2Nf"
DISCORD_WEBHOOK_URL_THREAD = "https://discord.com/api/webhooks/1473686602743287932/vBDGDdXom1PjyH6C9M93NZRNhIuDr9OmFgbm7PD3EdOLhiKCQ3hDOb9UNqRNPFq-4h6y"
THREAD_ID = 1473460056602447995

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


class SteadyRateLimiter:
    def __init__(self, rate_per_second: float):
        self.delay = 1 / rate_per_second
        self._lock = asyncio.Lock()
        self._last = 0.0

    async def wait(self):
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self._last

            if elapsed < self.delay:
                await asyncio.sleep(self.delay - elapsed)

            self._last = time.monotonic()


async def send_job_embed(
    job_name: str,
    stats: dict[str, int],
    total_batches: int,
    elapsed: float,
    total_users: int,
    failed_users,
    completed_at,
):
    color = 0xE74C3C if stats["failed"] > 0 else 0x2ECC71
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)
    fields = [
        {"name": "Total Users", "value": str(total_users), "inline": True},
        {"name": "Processed", "value": str(stats["processed"]), "inline": True},
        {"name": "Skipped", "value": str(stats["skipped"]), "inline": True},
        {"name": "Failed", "value": str(stats["failed"]), "inline": True},
        {"name": "Batches", "value": str(total_batches), "inline": True},
        {
            "name": "Duration",
            "value": f"{minutes}m {seconds}s",
            "inline": True,
        },
    ]

    if failed_users:
        limited = failed_users[:20]
        value = "\n".join(limited)

        if len(failed_users) > 20:
            value += f"\n...and {len(failed_users) - 20} more"

        fields.append(
            {
                "name": "Changed Users",
                "value": value,
                "inline": False,
            }
        )
    payload = {
        "embeds": [
            {
                "title": f"✅ {job_name} completed",
                "color": color,
                "fields": fields,
                "footer": {"text": "Last updated:"},
                "timestamp": datetime.now(UTC).isoformat(),
            }
        ]
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(DISCORD_WEBHOOK_URL, json=payload) as resp:
            if resp.status >= 400:
                text = await resp.text()
                logger.error(f"Webhook failed: {resp.status} - {text}")


async def log_job_run(
    job_name: str,
    stats: dict[str, int],
    total_batches: int,
    elapsed: float,
    failed_users: list[str],
    total_users: int,
):
    completed_at = int(datetime.now(UTC).timestamp())
    run_data = {
        "job": job_name,
        "total_users": total_users,
        "processed": stats["processed"],
        "skipped": stats["skipped"],
        "failed": stats["failed"],
        "failed_users": failed_users,
        "batches": total_batches,
        "duration_seconds": round(elapsed, 2),
        "completed_at": completed_at,
    }

    db.collection("meta").add(run_data)

    await send_job_embed(
        job_name,
        stats,
        total_batches,
        elapsed,
        total_users,
        failed_users,
        completed_at,
    )

    if job_name == "update_badges":
        await post_whale_leaderboard(completed_at)


class RollingRateLimiter:
    def __init__(self, max_requests: int, per_seconds: int):
        self.max_requests = max_requests
        self.per_seconds = per_seconds
        self.timestamps = deque()
        self._lock = asyncio.Lock()

    async def wait(self):
        async with self._lock:
            now = time.monotonic()

            # Remove expired timestamps
            while self.timestamps and now - self.timestamps[0] > self.per_seconds:
                self.timestamps.popleft()

            # If at limit → wait properly
            if len(self.timestamps) >= self.max_requests:
                sleep_time = self.per_seconds - (now - self.timestamps[0])

                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)

            # Add small jitter AFTER proper wait
            await asyncio.sleep(random.uniform(0.05, 0.15))

            self.timestamps.append(time.monotonic())


async def get_total_badges(session, limiter, ccid: str) -> int:
    url = f"{AQW_BADGES}{ccid}"

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
                badges = await resp.json()
                return len(badges)

        except ClientResponseError as e:
            if e.status == 429:
                wait_time = 2**attempt
                logger.warning(f"429 for {ccid}. Backing off {wait_time}s")
                await asyncio.sleep(wait_time)
            else:
                raise

    raise Exception(f"Max retries exceeded for {ccid}")


async def check_username(
    session, limiter, username: str
) -> dict[str, str | None] | None:
    url = f"{CCID_PAGE}{username}"

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            await limiter.wait()

            async with session.get(url) as resp:
                if resp.status == 200:
                    text = await resp.text()

                    data = parse_qs(text.lstrip("&"))

                    char_id = data.get("CharID", [None])[0]
                    if char_id is None:
                        return None

                    level_field = data.get("intLevel", [""])[0]

                    guild: str | None = None

                    if "---" in level_field:
                        level_str, guild = level_field.split(" --- ", 1)

                        guild = guild.strip()

                        if guild.endswith(" Guild"):
                            guild = guild.removesuffix(" Guild")

                        if not guild:
                            guild = None

                    return {
                        "ccid": char_id,
                        "guild": guild,
                    }

                if resp.status in (404, 403):
                    return None  # treat as "doesn't exist"

                if resp.status == 429:
                    raise ClientResponseError(
                        resp.request_info,
                        resp.history,
                        status=429,
                        message="Rate limited",
                    )

                # other weird cases
                logger.warning(f"Unexpected status {resp.status} for {username}")
                return None

        except ClientResponseError as e:
            if e.status == 429:
                wait_time = 2**attempt
                logger.warning(f"429 for {username}. Backing off {wait_time}s")
                await asyncio.sleep(wait_time)
            else:
                raise

    return None


async def process_user(
    user_doc,
    semaphore,
    session,
    limiter,
    stats,
    failed_users: list[str],
    check_ccid: bool,
):
    async with semaphore:
        user_id = user_doc.id

        try:
            user_data = user_doc.to_dict()

            if not user_data.get("verified"):
                stats["skipped"] += 1
                return None

            if check_ccid:
                ccid = user_data.get("ccid")
                if not ccid:
                    stats["skipped"] += 1
                    return None

                total_badges = await get_total_badges(session, limiter, ccid)

                logger.info(f"{user_id} → {total_badges} badges")
                stats["processed"] += 1

                return (
                    user_doc.reference,
                    {"total_badges": total_badges},
                )

            else:
                username = user_data.get("aqw_username")
                encoded_name = quote(username, safe="")
                if not username:
                    stats["skipped"] += 1
                    return None
                old_aqw_user: dict[str, str | None] = {
                    "ccid": user_data.get("ccid"),
                    "guild": user_data.get("guild"),
                }
                aqw_user = await check_username(session, limiter, encoded_name)
                stats["processed"] += 1

                # ❌ Case 1: Profile missing
                if not aqw_user:
                    logger.info(f"{username} no longer exists")

                    stats["failed"] += 1
                    failed_users.append(username)

                    return (
                        user_doc.reference,
                        {
                            "verified": False,
                            "guild": None,
                            "previous_igns": ArrayUnion([username]),
                        },
                    )

                # ✅ Case 2: Guild changed
                new_guild = aqw_user["guild"]
                old_guild = user_data.get("guild")

                if new_guild != old_guild:
                    logger.info(f"{username} guild changed → {old_guild} → {new_guild}")

                    return (
                        user_doc.reference,
                        {
                            "verified": True,
                            "guild": new_guild,
                        },
                    )

                # ✅ Case 3: No change
                logger.info(f"{username} unchanged")
                return None

        except Exception as e:
            logger.error(f"Failed for user {user_id}: {e}")
            stats["failed"] += 1
            return None


async def update_badges():
    start_time = time.time()
    logger.info("Starting badge update process...")

    users = list(db.collection("users").where("guild", "==", "Oath").stream())
    logger.info(f"Fetched {len(users)} users")

    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)

    stats = {"processed": 0, "skipped": 0, "failed": 0}
    failed_users: list[str] = []

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://account.aq.com/",
        "Connection": "keep-alive",
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        limiter = SteadyRateLimiter(REQUESTS_PER_SECOND)
        tasks = [
            process_user(
                user_doc, semaphore, session, limiter, stats, failed_users, True
            )
            for user_doc in users
        ]

        results = await asyncio.gather(*tasks)

    updates = [r for r in results if r]

    logger.info(f"{len(updates)} users ready for Firestore update")

    total_batches = 0

    for i in range(0, len(updates), BATCH_SIZE):
        batch = db.batch()
        chunk = updates[i : i + BATCH_SIZE]

        for ref, total_badges in chunk:
            batch.update(ref, {"total_badges": total_badges["total_badges"]})

        batch.commit()
        total_batches += 1
        logger.info(f"Committed batch {total_batches}")

    elapsed = time.time() - start_time

    logger.info(
        f"Processed: {stats['processed']} | "
        f"Skipped: {stats['skipped']} | "
        f"Failed: {stats['failed']} | "
        f"Batches: {total_batches}"
    )
    logger.info(f"Total time: {elapsed:.2f}s")
    await log_job_run(
        "update_badges", stats, total_batches, elapsed, failed_users, len(users)
    )


async def ensure_verified_field():
    logger.info("Checking users for missing 'verified' field...")

    users = list(db.collection("users").stream())

    missing_count = 0
    total_batches = 0

    for i in range(0, len(users), BATCH_SIZE):
        batch = db.batch()
        chunk = users[i : i + BATCH_SIZE]

        writes_in_batch = 0

        for user_doc in chunk:
            data = user_doc.to_dict() or {}

            updates = {}

            if "verified" not in data:
                updates["verified"] = False

            if "total_badges" not in data:
                updates["total_badges"] = 0

            if updates:
                batch.update(user_doc.reference, updates)
                missing_count += 1
                writes_in_batch += 1

        if writes_in_batch > 0:
            batch.commit()
            total_batches += 1
            logger.info(f"Committed batch {total_batches} ({writes_in_batch} updates)")

    logger.info(f"Finished. Added 'verified: False' to {missing_count} users.")


async def check_usernames():
    start_time = time.time()
    logger.info("Starting username confirmation process...")

    users = list(db.collection("users").where("verified", "==", False).stream())
    logger.info(f"Fetched {len(users)} users")

    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)

    stats = {"processed": 0, "skipped": 0, "failed": 0}
    failed_users: list[str] = []

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://account.aq.com/",
        "Connection": "keep-alive",
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        limiter = SteadyRateLimiter(REQUESTS_PER_SECOND)

        tasks = [
            process_user(
                user_doc, semaphore, session, limiter, stats, failed_users, False
            )
            for user_doc in users
        ]

        results = await asyncio.gather(*tasks)

    total_batches = 0
    batched_updates = [r for r in results if r]
    logger.info(f"{len(batched_updates)} users ready for Firestore update")

    for i in range(0, len(batched_updates), BATCH_SIZE):
        batch = db.batch()
        chunk = batched_updates[i : i + BATCH_SIZE]

        for ref, update_data in chunk:
            batch.update(ref, update_data)

        batch.commit()
        total_batches += 1
        logger.info(f"Committed batch {total_batches}")

    elapsed = time.time() - start_time

    logger.info(
        f"Processed: {stats['processed']} | "
        f"Skipped: {stats['skipped']} | "
        f"Failed: {stats['failed']} | "
        f"Batches: {total_batches}"
    )
    logger.info(f"Total time: {elapsed:.2f}s")
    await log_job_run(
        "verify_usernames",
        stats,
        total_batches,
        elapsed,
        failed_users,
        len(users),
    )


async def delete_webhook_message(message_id: str):
    delete_url = f"{DISCORD_WEBHOOK_URL_THREAD}/messages/{message_id}?thread_id={THREAD_ID}&wait=true"

    async with aiohttp.ClientSession() as session:
        async with session.delete(delete_url) as resp:
            if resp.status not in (200, 204):
                text = await resp.text()
                logger.error(f"Delete failed: {resp.status} - {text}")


async def post_whale_leaderboard(updated_at: int):
    whale_doc_ref = db.collection("meta").document("whale_leaderboard")
    snapshot = whale_doc_ref.get()

    previous_positions = {}
    previous_message = None

    if snapshot.exists:
        previous_positions = snapshot.to_dict().get("positions", {})
        previous_message = snapshot.get("message_id")

    if previous_message:
        await delete_webhook_message(str(previous_message))

    users = (
        db.collection("users")
        .where(filter=FieldFilter("guild", "==", "Oath"))
        .order_by("total_badges", "DESCENDING")
        .limit(30)
        .stream()
    )

    medals = ["🥇", "🥈", "🥉"]
    lines = []
    new_positions = {}
    UNKNOWN_POSITION = 31
    for i, doc in enumerate(users):
        position = i + 1
        display_name = doc.get("aqw_username")
        badges = doc.get("total_badges")

        new_positions[display_name] = position

        previous_position = previous_positions.get(display_name, UNKNOWN_POSITION)

        delta = previous_position - position

        # Determine movement indicator
        if previous_position == UNKNOWN_POSITION:
            movement = f"🆕"
        elif delta > 0:
            movement = f"<:greenUp:1475306546018648290> +{delta}"
        elif delta < 0:
            movement = f"<:redDown:1475306580814598185> {delta}"
        else:
            movement = ""

        if i < 3:
            prefix = medals[i]
        else:
            prefix = f"`{position:02}`"

        lines.append(f"{prefix} **{display_name}** — `{badges}` badges {movement}")

    color = 0xD1AE77
    if not lines:
        return discord.Embed(
            title="🐋 Pod of Whales",
            description="No badge data yet.",
            color=color,
        )

    embed = discord.Embed(
        title="🐋 Pod of Whales",
        description="\n".join(lines),
        color=color,
    )

    embed.timestamp = datetime.fromtimestamp(updated_at, UTC)
    embed.set_footer(text="Last updated")

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{DISCORD_WEBHOOK_URL_THREAD}?thread_id={THREAD_ID}&wait=true",
            json={"embeds": [embed.to_dict()]},
        ) as resp:
            if resp.status >= 400:
                text = await resp.text()
                logger.error(f"Webhook failed: {resp.status} - {text}")
                return None

            data = await resp.json()
            message_id = data["id"]

            whale_doc_ref.set(
                {
                    "message_id": message_id,
                    "updated_at": datetime.now(UTC),
                    "positions": new_positions,
                }
            )


if __name__ == "__main__":
    asyncio.run(check_usernames())
    # asyncio.run(update_badges())
    # asyncio.run(post_whale_leaderboard(1771810402))
