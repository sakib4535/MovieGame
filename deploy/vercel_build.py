"""Vercel-only build checks. Never modifies application files or database records."""
from sqlalchemy.engine import make_url
from app.catalog import load_sources
from app.config import ROOT, Settings


def main():
    settings = Settings()
    if settings.environment != 'production':
        raise SystemExit('Set APP_ENV=production in Vercel before deploying.')
    settings.validate()
    database = make_url(settings.database_url)
    if database.query.get('sslmode') not in ('require', 'verify-ca', 'verify-full'):
        raise SystemExit('DATABASE_URL must use hosted PostgreSQL with sslmode=require or stronger.')
    if not settings.redis_url.startswith('rediss://'):
        raise SystemExit('REDIS_URL must be a TLS Redis connection URL (rediss://), not an HTTP REST URL.')
    if settings.pool_size > 2:
        raise SystemExit('Set DB_POOL_SIZE=1 (or 2) to bound connections per Vercel instance.')
    for secret in (settings.rate_secret, settings.metrics_token):
        if 'REPLACE_' in secret:
            raise SystemExit('Replace the example secret placeholders in Vercel Environment Variables.')
    movies = load_sources(ROOT / 'data')
    print(f'Vercel checks passed: {len(movies)} films; runtime data and frontend assets are present.')
    print('Hosted PostgreSQL must already be initialized with python -m app.manage init.')


if __name__ == '__main__':
    main()
