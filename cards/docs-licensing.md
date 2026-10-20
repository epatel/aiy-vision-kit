# docs-licensing

Decision: what third-party material may be committed to this public repo, and how the rest is referenced.

## The choice

- **Committed** (with license files kept): Google's AIY repo snapshot (Apache-2.0 / GPL-2.0), Raspberry Pi documentation AsciiDoc (CC BY-SA 4.0,
  `docs/reference/rpi-documentation/LICENSE.md`), picamera2 source (BSD-2-Clause), Linux kernel doc pages (GPL-2.0), the dkms man page, gpiozero and libgpiod docs,
  the protobuf news page.
- **Links only** (local copies may live in the gitignored `docs/local-only/`): Raspberry Pi blog posts (they include reader comments), pages from
  `aiyprojects.withgoogle.com`, and the Picamera2 manual PDF. No redistribution license was found for any of them.
- **Never committed:** the Myriad firmware and models (fetched, see `port/fetch-binaries.sh`), and `vendor/`.
- The repo has no license of its own. `port/drivers/` inherits GPL-2.0 and `port/python/` Apache-2.0 from Google's code (README "Licensing").

## Alternatives considered

- **Commit everything fetched:** fine for a private repo, not for a public one.
- **Drop `docs/` entirely:** loses offline reference material that agents and people use during porting work.

## Why this won

It keeps the useful offline references with clear terms, and before the repo went public it removed (from the whole history, not just the latest commit) the files with unclear terms.

## When adding material to docs/

- Check the license first. Keep the upstream `LICENSE` file and a `COMMIT` file (repos) or a `source:` header (pages).
- No clear license: add a link in `docs/README.md` and keep the copy in `docs/local-only/`.
- Don't trim license files when pruning a snapshot (an earlier prune deleted the Raspberry Pi docs' `LICENSE.md`; it was restored).
