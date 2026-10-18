# Bilingual layout verification — 19 October 2026

- Named eight-trait card moved to the top-right of desktop results; it appears before the movie card on small screens. Compact header, character, movie, score and all eight bars are contained in one card.
- Navigation links, previous/next controls, share buttons and language selector use the existing light green colour. The language selector is last in the navigation bar.
- Complete English/Bangla presentation coverage: 1,126 movies, 2,282 character profiles, 54 prompts, 321 answer options, all themes/trait labels, UI/privacy text, five reason explanations, public share metadata and PNGs. English answers, IDs, seed, scoring, and database schema remain canonical and unchanged.
- Bangla metadata is bundled as static display assets. Catalog views/search strings are prepared once per process. No runtime translation network calls. Private localized-result reads use the existing UUID header and `Cache-Control: no-store`; language selection is outside the idempotency payload.
- **37 automated tests passed; 1 PostgreSQL/Redis integration test skipped** because those external services were unavailable. New tests verify full Bangla coverage, unchanged catalog fingerprint, exact question/option IDs, selected-answer quotes, unchanged scores/stored results/replays, Bangla search, share privacy/expiry behaviour inherited from existing tests, PNG dimensions, and Bengali glyph shaping.
- Browser verification passed: full Bangla home page, language switching with the selected survey answer preserved, complete 15-question flows in both game modes, named result with eight bars in one viewport, Bangla library search, copy-link flow, public share page and English/Bangla switch. Downloaded 1200×630 Bangla PNG visually checked with joined letters, name and eight bars. Final desktop result screenshot saved with the task artifacts. Mobile CSS ordering is implemented; a separate device viewport was not available in the browser tool.
- Bengali image text uses HarfBuzz/FreeType so Windows builds without Pillow Raqm still render conjuncts correctly. Open font licenses remain bundled. JavaScript syntax checks passed.
- Live database is backed up before copying the reviewed files; no database replacement or schema migration is needed. Existing startup scripts, Vercel routing/runtime settings and canonical catalog/survey data are preserved.
- No social account was posted to. Actual social previews/device share sheets, public Vercel deployment, production PostgreSQL/Redis failover and ten-million-user throughput still require the corresponding infrastructure.

The earlier expansion record below is retained as history. Its browser limitation was resolved by the bilingual update's browser checks above.

## Expansion verification — 19 October 2026

- **537 added films**, for **1,126 films and 2,282 character profiles**: 994 Hollywood, 45 Bangladeshi, 87 Japanese anime.
- Every film has **two or four named characters**: 1,111 films have two; 15 ensembles have four. All original film metadata and original character profiles were preserved. Unique title/year keys, valid trait scores, and category membership passed structural checks.
- **118 film references individually checked**; 1,008 remain explicitly unverified. Cast research also covered the existing films, including the Bangladeshi entries. Personality scores and themes are editorial interpretations.
- **1,108 actual Wikimedia artwork references**, with attribution/file-page links; **18 original cover-art fallbacks**. Matching performs no external metadata calls. Failed reference images fall back to generated covers.
- Two separate **27-question banks**, each selecting 15 questions per seed. Both cover all eight traits, include two story-value questions, and shuffle answer order. Character Game matches across the complete catalog. Stable option IDs keep shuffled positions from changing scores.
- Matching uses 90% equal-weight eight-trait similarity and 10% editorial story-value signals. Five explanations quote actual answers. Close matches show alternatives; this game does not claim exact psychological identification.
- **31 automated tests passed; 1 real PostgreSQL/Redis integration test skipped** because those services were unavailable. Covered both modes, variation, invalid/stale requests, rate limits, dependency failure, concurrent replays, concurrent share creation, public-share privacy/escaping/expiry, PNG dimensions, artwork fallback, and migration preservation.
- The version-one migration test preserved an existing result and old survey record, appended catalog data, and replayed the identical old idempotent request after upgrading. Repeated migration passed. Staging source/database fingerprints matched: `bea334eaa576e57db1afba7d`.
- JavaScript syntax checks passed. The 1200×630 share-card PNG was rendered and visually inspected: display name, character, film, affinity, and all eight trait bars. Inter and Noto Sans Bengali fonts and open licenses are bundled.
- Local startup scripts, Python runtime selection, and Vercel routing configuration remain unchanged. Deployment instructions cover the data upgrade and PUBLIC_BASE_URL for custom-domain share metadata.
- **Browser layout verification could not run:** automatic approval review blocked the localhost preview because its approval service reported a usage limit. No alternate browser path was used. This remains a visual QA limitation.
- Actual Facebook preview rendering and Instagram/device share-sheet delivery require a public HTTPS deployment and the user's social apps. No real social account was posted to or tested. Instagram uses native file sharing or a downloadable PNG; a browser cannot force it to publish.
- Vercel deployment, actual PostgreSQL/Redis failover, container runtime, and ten-million-user throughput remain unverified on hosting infrastructure. No production capacity guarantee is made.

The Python test client emitted a third-party HTTPX deprecation warning; tests passed with the existing pinned dependency.

- The previous version's full browser flow had passed. The new expansion has the automated verification listed above; it is not described as browser-tested.


Installed-copy verification: 1126 films, 2282 characters; 4 pre-existing saved results preserved. Database backup: `E:\vscode-git\MovieGame\backups\moviegame-before-expansion-2026-10-19-d0deb469.db`. Startup scripts and Vercel routing/runtime files stayed unchanged.
