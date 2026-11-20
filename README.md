# remmina-copr

Source: https://github.com/wrouesnel/remmina-copr
Packages: https://copr.fedorainfracloud.org/coprs/wrouesnel/remmina-el8/

Current Remmina and FreeRDP 3 for EL8 (RHEL/Alma/Rocky 8), with the full RDP
GFX pipeline including H.264 (AVC420/AVC444). EPEL8 stops at Remmina 1.4.33
on FreeRDP 2.11.

## Packages

- `freerdp3.spec`: FreeRDP 3.33.1, derived from Fedora's spec. It installs
  alongside RHEL's FreeRDP 2: packages are `freerdp3`, `freerdp3-libs`,
  `libwinpr3` and so on, binaries are versioned (`xfreerdp3`), and uwac is
  linked statically.
  - H.264 decoding uses OpenH264, loaded at runtime (`WITH_OPENH264_LOADING`).
    The build only uses OpenH264's API headers (`sources/openh264-*`, v2.7.0,
    BSD-2-Clause). No codec code is shipped.
  - `freerdp3-install-openh264` (run as root) downloads Cisco's patent-licensed
    binary (2.7.0, `libopenh264.so.8`, sha256 pinned) into
    `/usr/lib64/openh264-cisco`. Without it, FreeRDP 3 doesn't advertise H.264
    and servers fall back to RemoteFX/progressive.
- `remmina.spec`: Remmina 1.4.44, based on Fedora's EPEL8 spec, with the RDP
  plugin built against `freerdp3` (`--without freerdp3` builds against RHEL's
  FreeRDP 2.11).
  - Builds out of source. 1.4.44's `cmake/FindKDEProtocols.cmake` writes an
    unprocessed `config.h` into the build root, and in EL8's in-source cmake
    build that copy wins over `generated/config.h`.
  - `0001`: missing `fcntl.h`/`errno.h` includes.
  - `0002`: `G_SOURCE_FUNC` fallback (GLib 2.56) and a guard around
    `spice_main_channel_update_display_mm` (spice-gtk 0.38).

## Installing (COPR)

    dnf install epel-release && dnf config-manager --set-enabled powertools
    dnf copr enable wrouesnel/remmina-el8
    dnf install remmina remmina-plugins-rdp
    freerdp3-install-openh264

## Building locally

    ./build.sh freerdp3.spec
    cp out/freerdp3/x86_64/*.rpm out/repo/
    ./build.sh remmina.spec

`build.sh` runs `rpmbuild` in an `almalinux:8` container (podman) with EPEL and
PowerTools enabled. It downloads Source0 into `sources/`. RPMs in `out/repo/`
are offered to the build as a local repo.

## Releasing

Releases go to COPR through GitHub Actions (`.github/workflows/release.yml`):

1. Bump `Version`/`Release` in the spec and add a `%changelog` entry. Check it
   builds with `./build.sh <spec>`.
2. Commit, then push a tag named `<package>-<version>-<release>`, without the
   dist tag:

       git tag -s remmina-1.4.44-3 -m "remmina 1.4.44-3"
       git push origin main remmina-1.4.44-3

3. The workflow checks the tag against the spec, builds the SRPM on
   AlmaLinux 8, builds it in COPR (`wrouesnel/remmina-el8`), waits for the
   result, and creates a GitHub release with the SRPM and the COPR build link.

Release `freerdp3` first when both change: Remmina builds against the
`freerdp3` already in COPR. To build an SRPM without publishing, run the
workflow by hand (Actions → Release to COPR → Run workflow) and leave
"Submit" unticked. The SRPM is kept as a workflow artifact.

The workflow needs a `COPR_CONFIG` repository secret holding a copr-cli
config file (`~/.config/copr`) for an account that can build in the project.
COPR API tokens expire after about 180 days, so update the secret when the
token is renewed.

## Verified

In an AlmaLinux 8 container with RHEL's FreeRDP 2 also installed:
`freerdp-shadow-cli3` served an Xvfb display, and both `xfreerdp3 /gfx:AVC444`
and Remmina (colour depth "GFX AVC444") received and decoded
`RDPGFX_CODECID_AVC444v2` frames through Cisco OpenH264 without visible
corruption.
