# Publication, recovery, and rollback

The publication workflow deliberately separates updating, review, and publishing.

## Normal update

1. Start with a clean working tree on the publication branch.
2. Run `./update.sh`. It fast-forwards the branch, runs tests and normalized-data parity checks,
   updates active sources, renders the site, and validates source health.
3. Review `git diff`, especially `data/`, `docs/data/source-health.json`, and the generated site.
4. Run `./publish.sh "Describe the data update"`. It repeats the blocking validation, stages only
   `data/` and `docs/`, refuses unrelated changes, and does not create an empty commit.

Page-hit collection is deliberately separate. Run `./update-pagehits.sh` only when that auxiliary
counter should be refreshed.

Chart timestamps and “today” markers use the newest observation date, not the wall clock. Therefore
an unchanged dataset renders identically and does not create a publication merely because another
day has passed. Set `CORONADATA_BUILD_DATE=YYYY-MM-DD` only for an intentional reproducible override.

## Failed source or validation

Do not bypass a blocking source-health or schema error. The downloader installs a cache file only
after validation, so the previous valid cache should still be present. Inspect:

- `cache/build-report.json` for the build decision;
- `cache/source-health.json` or `docs/source-status.html` for source-level dates and messages;
- `cache/errors.log` for legacy renderer warnings;
- `cache/raw/<source>/` for immutable downloaded snapshots.

Fix the adapter or source configuration, rerun `./update.sh`, and publish only after the checks pass.

## Restore a source snapshot

Copy the intended read-only snapshot from `cache/raw/<source>/` to a new temporary file, validate it
with the relevant parser/test, then replace the cache through the normal adapter workflow. Never edit
the archived snapshot in place. If the external archive from Phase 1 is required, restore it outside
the repository first and compare its manifest before copying individual files.

## Roll back a publication

Published updates are ordinary Git commits. Prefer a new `git revert <bad-commit>` commit so the
history and reason remain visible. Push the revert only after running `./dev.sh` and an offline
`./render.sh`. Do not rewrite published history, delete historical data, or reset the branch to hide
the failed publication.
