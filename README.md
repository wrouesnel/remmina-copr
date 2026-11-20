# remmina-copr

Remmina backported to EL8 (RHEL/Alma/Rocky 8). EPEL8 stops at 1.4.33; this
builds the current upstream release against EL8's own libraries.

- `remmina.spec`: based on the Fedora EPEL8 spec, moved to 1.4.44.
  - Builds out of source. 1.4.44's `cmake/FindKDEProtocols.cmake` writes an
    unprocessed `config.h` into the build root, and in EL8's in-source cmake
    build that copy wins over `generated/config.h`.
  - `0001`: missing `fcntl.h`/`errno.h` includes.
  - `0002`: `G_SOURCE_FUNC` fallback (GLib 2.56) and a guard around
    `spice_main_channel_update_display_mm` (spice-gtk 0.38).
  - Builds against RHEL's FreeRDP 2.11.7 by default; `--with freerdp3` builds
    the RDP plugin against FreeRDP 3 instead.

## Building

    ./build.sh remmina.spec              # RPMs + SRPM in out/remmina/
    ./build.sh remmina.spec --with freerdp3

`build.sh` runs `rpmbuild` in an `almalinux:8` container (podman) with EPEL and
PowerTools enabled. It downloads Source0 into `sources/`. RPMs placed in
`out/repo/` are offered to the build as a local repo.
