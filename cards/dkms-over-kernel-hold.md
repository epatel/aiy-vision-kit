# dkms-over-kernel-hold

Decision: install the Vision Bonnet drivers as one DKMS package and let kernel upgrades rebuild them, rather than pinning the kernel with `apt-mark hold` by default.

## The choice

`install.sh` registers `aiy-vision-kit` with DKMS (`AUTOINSTALL=yes`), so a new kernel's postinst hook rebuilds the modules. Holding the kernel is opt-in: `install.sh --hold-kernel`.

## Alternatives considered

- **Hold the kernel and headers** (the original plan): nothing can break on `apt upgrade`, but the card never gets kernel security fixes, and the hold is easy to forget.
- **Hand-built modules in `/lib/modules/<ver>/updates/`:** what development used. They vanish on every kernel update.
- **Upstream the drivers:** the right long-term answer, but far more work than this port.

## Why this won

- The same driver source already builds on 6.12 (Bookworm) and 6.18 (Trixie) with a few `LINUX_VERSION_CODE` checks, so automatic rebuilds are likely to keep working.
- When a rebuild fails, it fails loudly in `dkms status` and the apt log, and the fix is a source change in one place.

## Costs accepted

- If a future kernel breaks the build, the bonnet stops working after the reboot until the drivers are patched. Check `/usr/sbin/dkms status` after upgrades.
- DKMS builds for every installed kernel flavour with headers present (v6, v7, v7l on Raspberry Pi OS), which is slow on a Pi Zero.
- `install.sh` rebuilds on every run (about 10 minutes), even when nothing changed.

## When to revisit

- A kernel update breaks the build and a fix isn't quick: recommend `--hold-kernel` in the README until it is.
- Rebuild time becomes a problem: skip the build in `install.sh` when the installed version's source matches.
