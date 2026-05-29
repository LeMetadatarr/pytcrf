# TODO

- **CI** — no `.github/workflows/` yet. Wire up the `gh-automations` reusable
  workflows (referenced at `@dev`): alpha on PR→`dev`, release PR→`master`.
  Versions bump from conventional-commit prefixes; do not add a version job.
- **pyromhacking join** — add a helper that maps a `tcrf_title` to its
  pyromhacking entry (or document the join key) for the cross-source linking
  dataset task in `docs/dataset.md`.
- **Richer platform detection** — `_parse.platforms_from_wikitext` reads the
  `{{bob}}` infobox `system`/`platform`/`console` params; the category tree is
  authoritative. Reconcile multi-system pages where the two disagree.
- **Sub-pages** — large games split content into `/Unused Graphics` etc.
  sub-pages (the `Sub-Pages` section links them). Optionally follow and merge
  sub-page sections into the parent `GamePage`.
- **Section text in `iter_games`** — currently one `parse` call per section. A
  `prop=parsetree`/single-fetch path could cut calls for big pages.
