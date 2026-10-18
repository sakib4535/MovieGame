"""python -m app.manage init|upgrade|validate|prune|export-schema"""
import argparse
import json
from datetime import datetime, timezone
from sqlalchemy import select, delete
from sqlalchemy.schema import CreateTable, CreateIndex
from sqlalchemy.dialects import postgresql
from .config import ROOT, Settings
from .catalog import load_sources, Catalog
from .database import make_engine, initialize, submissions, shares, metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['init', 'upgrade', 'validate', 'prune', 'export-schema'])
    args = parser.parse_args()
    settings = Settings()
    settings.validate()
    if args.command in ('init', 'upgrade', 'validate'):
        source = load_sources(ROOT / 'data')
        catalog = Catalog(source)
        if args.command in ('init', 'upgrade'):
            engine = make_engine(settings)
            initialize(engine, source, upgrade=args.command == 'upgrade')
            engine.dispose()
        print(json.dumps({'films': len(source), 'characters': len(catalog.characters),
                          'categories': catalog.counts, 'version': catalog.version,
                          'source_verified': sum(m['source_verified'] for m in source)}))
    elif args.command == 'prune':
        engine = make_engine(settings)
        count = 0
        for table, primary in ((shares, shares.c.token), (submissions, submissions.c.key_hash)):
            for _ in range(100):
                with engine.begin() as conn:
                    keys = select(primary).where(table.c.expires_at < datetime.now(timezone.utc)).limit(1000)
                    deleted = conn.execute(delete(table).where(primary.in_(keys))).rowcount
                count += deleted
                if deleted < 1000:
                    break
        engine.dispose()
        print(json.dumps({'deleted': count, 'batch_limit_per_table': 100000}))
    else:
        dialect = postgresql.dialect()
        statements = [str(CreateTable(t).compile(dialect=dialect)) + ';' for t in metadata.sorted_tables]
        statements += [str(CreateIndex(i).compile(dialect=dialect)) + ';' for t in metadata.sorted_tables for i in t.indexes]
        (ROOT / 'deploy' / 'schema.sql').write_text('-- MovieGame schema v2; generated from app/database.py\n' + '\n'.join(statements), encoding='utf-8')


if __name__ == '__main__':
    main()
