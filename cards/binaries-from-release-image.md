# binaries-from-release-image

Decision: the Myriad firmware and the models are not committed. `port/fetch-binaries.sh` extracts them from Google's official AIY system image on GitHub releases.

## The choice

Rebuild `vendor/aiy-binaries.tgz` (`lib/firmware/myriad_fw.mvcmd` + 15 files in `opt/aiy/models/`) from
`https://github.com/google/aiyprojects-raspbian/releases/download/v20210402/aiyprojects-2021-04-02.img.xz`, checked against the release's `.sha256`.
`install.sh` checks the firmware's own SHA-256 (`438a1fc9…d1d3`).

## Alternatives considered

- **Commit the binaries:** they are Google's, the license is unclear, and the repo is public.
- **Google's apt repo** (`packages.cloud.google.com/apt aiyprojects-stable`, which used to ship `aiy-vision-firmware` / `aiy-models` .debs): returns 404 since at least 2026-10-20.
- **A third-party mirror:** none found. GitHub code search only turns up copies of the driver source, and a web search found nothing.
- **Copy from a card running the official image** (`dpkg -L aiy-vision-firmware aiy-models | … tar`): works, and that's how the first archive was made. But it needs that card,
  so it stays documented as the fallback.
- **Mount the image:** needs root and Linux. `debugfs` on the carved-out partition needs neither, and runs on macOS through Docker or Homebrew `e2fsprogs`.

## Why this won

The release image is the one public, stable, checksummed source left. The extracted files are byte-for-byte identical to the ones copied from a running card (all 16 compared).
The script is resumable, caches the download, and avoids root, mounting and Linux on the host.

## When to revisit

- GitHub removes the release asset, or the `.sha256` stops matching: fall back to a card (or keep `vendor/cache/*.img.xz` safe somewhere).
- Google publishes the files elsewhere under a clear license: download those instead and maybe commit them.
- A newer official image appears with different firmware: the pinned SHA-256s in `install.sh` and `fetch-binaries.sh` need updating together.
