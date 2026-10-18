import os
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Settings:
    environment: str = os.getenv('APP_ENV', 'development')
    database_url: str = os.getenv('DATABASE_URL', f'sqlite:///{ROOT / "moviegame.db"}')
    redis_url: str = os.getenv('REDIS_URL', '')
    rate_secret: str = os.getenv('RATE_SECRET', 'local-development-only')
    metrics_token: str = os.getenv('METRICS_TOKEN', '')
    pool_size: int = int(os.getenv('DB_POOL_SIZE', '10'))
    rate_limit: int = int(os.getenv('RATE_LIMIT_PER_MINUTE', '30'))
    retention_days: int = int(os.getenv('RETENTION_DAYS', '30'))
    max_inflight: int = int(os.getenv('MAX_INFLIGHT', '64'))
    public_base_url: str = (os.getenv('PUBLIC_BASE_URL') or
                           (f'https://{os.environ["VERCEL_URL"]}' if os.getenv('VERCEL_URL') else '')).rstrip('/')

    def validate(self):
        if self.public_base_url:
            from urllib.parse import urlparse
            public = urlparse(self.public_base_url)
            if not public.netloc or public.scheme not in ('https', 'http') or public.path not in ('', '/') or public.query or public.fragment or public.username:
                raise ValueError('PUBLIC_BASE_URL must be the website origin, without a path or credentials.')
            if self.environment == 'production' and public.scheme != 'https':
                raise ValueError('PUBLIC_BASE_URL must use HTTPS in production.')
        if self.environment == 'production':
            if not self.database_url.startswith('postgresql+psycopg://'):
                raise ValueError('Production requires PostgreSQL with psycopg.')
            if not self.redis_url or len(self.rate_secret) < 32 or len(self.metrics_token) < 32:
                raise ValueError('Production requires Redis and random secrets of at least 32 characters.')
        if not (1 <= self.pool_size <= 100 and 1 <= self.max_inflight <= 1000):
            raise ValueError('Invalid connection or concurrency budget.')
        if not (1 <= self.retention_days <= 365 and self.rate_limit >= 1):
            raise ValueError('Invalid retention or rate limit.')
