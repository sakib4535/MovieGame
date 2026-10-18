# Deploy MovieGame to Vercel

This setup uses the existing FastAPI app at `app/main.py`. It supports both game modes, the expanded movie catalog, and named share-result pages. Existing local startup scripts are unchanged.

## 1. Prepare persistent services

Create a hosted **PostgreSQL database** and a hosted **Redis database**. Place them near the Vercel function region you select in the dashboard. Vercel runs the web app and API; the Docker Compose database, Redis server, and Nginx container do not run on Vercel.

- PostgreSQL: use the URL format shown in `.env.vercel.example`. Add `?sslmode=require` if there are no query parameters, or `&sslmode=require` otherwise. URL-encode special characters in the username/password. If your provider supplies `postgres://` or `postgresql://`, change only that prefix to `postgresql+psycopg://`.
- Redis: use the provider's TLS connection URL, beginning `rediss://`. The app uses the Redis protocol, so an HTTP REST URL/token is insufficient. Keep the provider's actual hostname and port.
- Start with `DB_POOL_SIZE=1` per function instance. Use a provider-supported pooled PostgreSQL endpoint if it supports this app's psycopg prepared statements and PostgreSQL connection `options` for timeouts. Otherwise use the direct PostgreSQL endpoint initially and keep aggregate function-instance connections within its limit.

The bundled SQLite database remains your local development database. It is excluded from Vercel uploads. Durable idempotency records are stored in hosted PostgreSQL.

## 2. Set environment variables

In Vercel, create/import the project and open **Settings → Environment Variables**. Add these values for **Production**. Add separate database/Redis credentials for **Preview** if you want preview deployments; they must also use `APP_ENV=production` so the app does not attempt local SQLite writes.

| Name | Value |
|---|---|
| `APP_ENV` | `production` |
| `DATABASE_URL` | Your PostgreSQL URL with the `postgresql+psycopg://` prefix and TLS |
| `REDIS_URL` | Your Redis TLS URL, starting `rediss://` |
| `RATE_SECRET` | A random secret of at least 32 characters |
| `METRICS_TOKEN` | A different random secret of at least 32 characters |
| `DB_POOL_SIZE` | `1` |
| `MAX_INFLIGHT` | `32` |
| `RATE_LIMIT_PER_MINUTE` | `30` |
| `RETENTION_DAYS` | `30` |
| `PUBLIC_BASE_URL` | Your public HTTPS website origin, such as `https://your-project.vercel.app`; update after adding a domain |

`.env.vercel.example` is a reference, not a file to fill with credentials. Generate each secret locally with `python -c "import secrets; print(secrets.token_hex(32))"`, then paste its value into the dashboard. Real credentials belong in Vercel Environment Variables.

The build check rejects missing production settings, example secret placeholders, insecure connection URLs, and oversized per-instance connection pools. It validates files without opening connections or changing your database.

## 3. Initialize the hosted database once

In a new PowerShell terminal, run the following. Enter the same service credentials/secrets you configured in Vercel when prompted; input is hidden and kept in the terminal process environment.

```powershell
cd E:\vscode-git\MovieGame
$env:APP_ENV = 'production'
$env:DB_POOL_SIZE = '1'
foreach ($name in @('DATABASE_URL', 'REDIS_URL', 'RATE_SECRET', 'METRICS_TOKEN')) {
    $value = Read-Host $name -AsSecureString
    $plain = [System.Net.NetworkCredential]::new('', $value).Password
    [Environment]::SetEnvironmentVariable($name, $plain, 'Process')
    $plain = $null
}
.\.venv\Scripts\python.exe -m app.manage init
```

Initialization creates the production schema and seeds the 1,126-film catalog. It is safe to repeat for the same catalog; it refuses to overwrite a different catalog version. Confirm the success output, then close this terminal to discard the environment. If the command fails, resolve the connection/permissions issue before deploying. The application does not migrate or seed production databases during requests or cold starts.

## 4. Deploy

1. Put **MovieGame itself** in a Git repository and import that repository into Vercel. If it is a subfolder in a larger repository, select that folder as the project's **Root Directory**. Never use `web` as the root: it would leave out the API.
2. Use the **FastAPI** framework preset. Vercel reads `vercel.json`, `.python-version`, and the existing Python requirements. Keep **Output Directory** unset; there is no frontend build directory.
3. Leave **Install Command** on its automatic setting so Vercel installs the existing `requirements.txt` with its Python runtime. The configured build command is `python -m deploy.vercel_build`. Use the repository settings rather than adding dashboard overrides.
4. Deploy after the environment variables and hosted database are ready. If an initial import build failed before you entered the variables, redeploy it after completing those steps.
5. Check `/health/ready`, `/api/v1/survey`, the full 15-question reveal, and the searchable character library on the returned HTTPS `*.vercel.app` address.

The current FastAPI entrypoint is supported directly. No catch-all rewrite, extra `api/index.py`, custom domain URL, CORS change, or frontend modification is needed. The browser uses relative API/asset paths. Static middleware/security behavior is preserved. A deployment build is not an infrastructure load test.

## 5. Add your domain later

After buying a domain, open **Vercel Project → Settings → Domains → Add Domain**. Add your root domain and `www` hostname, select the preferred one, and redirect the other to it. At your domain registrar, enter the **exact DNS records Vercel shows for your project**; do not copy fixed IP addresses or CNAME values from another project. Wait for Vercel's domain and HTTPS checks to succeed.

You can keep DNS at your current registrar and change the website records there. Keep existing email MX/TXT records. The app's relative paths work on the new domain without editing the game or changing the database. Update `PUBLIC_BASE_URL` and redeploy so share-image metadata uses the preferred domain. Session progress is browser-origin specific, so an in-progress quiz on the old hostname does not automatically transfer to the new one.

## Retention and operation

Vercel replaces the Compose API containers and Nginx for this hosting path. It does not run the Compose/Kubernetes hourly cleanup jobs. Schedule the existing `python -m app.manage prune` command on a trusted external scheduled runner with the same production environment, or arrange equivalent bounded expiry cleanup with your database provider. Monitor expired-row backlog; the command removes at most 100,000 expired results per run. Do this before public launch so the 30-day retention setting is enforced.

Keep preview credentials separate from production. Choose a function region near your databases, monitor database connections and 429/503 rates, and run the existing load test against staging before scaling traffic. Vercel autoscaling does not remove PostgreSQL/Redis capacity limits. No hosting account, database service, public deployment, or domain has been created by these local changes.

## References

- [Vercel FastAPI entrypoints, lifespan, and function settings](https://vercel.com/docs/frameworks/backend/fastapi)
- [Vercel Python versions and dependencies](https://vercel.com/docs/functions/runtimes/python)
- [Vercel deployment configuration](https://vercel.com/docs/project-configuration/vercel-json)
- [Vercel custom domain setup](https://vercel.com/docs/domains/working-with-domains/add-a-domain)

Configuration and local regression checks can run without a Vercel account. A real Vercel build and hosted database/Redis connectivity still need to be verified after the services and project environment are configured.


## Existing version-one deployments

Back up the hosted database, then run `python -m app.manage upgrade` with the same production credentials before deploying this expansion. This preserves existing results while adding 537 films, additional characters, artwork metadata, the second survey edition, and public share snapshots. New empty databases can still use `init`. Both private results and public share snapshots are removed by `python -m app.manage prune`. Facebook previews need an unrestricted public HTTPS `/s/<token>` page and its `/card.png`; Vercel Preview Deployment Protection can prevent social crawlers from accessing previews. Test sharing on the production domain.
