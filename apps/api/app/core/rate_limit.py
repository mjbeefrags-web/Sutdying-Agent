import hashlib

from redis import Redis
from redis.exceptions import RedisError

from apps.api.app.core.config import get_settings
from apps.api.app.core.errors import AppError


def enforce_rate_limit(scope: str, identity: str, limit: int, window_seconds: int) -> None:
    identity_hash = hashlib.sha256(identity.encode("utf-8")).hexdigest()
    key = f"rate-limit:{scope}:{identity_hash}"
    client = Redis.from_url(get_settings().redis_url, socket_connect_timeout=1, socket_timeout=1)
    try:
        count = client.incr(key)
        if count == 1:
            client.expire(key, window_seconds)
        if count > limit:
            ttl = max(client.ttl(key), 1)
            raise AppError(
                429,
                "rate_limited",
                "Too many requests. Please try again later.",
                headers={"Retry-After": str(ttl)},
            )
    except RedisError as exc:
        raise AppError(
            503, "rate_limit_unavailable", "Request protection is temporarily unavailable."
        ) from exc
    finally:
        client.close()
