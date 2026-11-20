#!/bin/bash
# Build an SRPM/RPMs for EL8 inside an AlmaLinux 8 container.
# Usage: ./build.sh <spec> [extra rpmbuild args, e.g. --with freerdp3]
# Results land in ./out/<spec name>/. RPMs already in ./out/repo are made
# available as a local dnf repo (so remmina can build against our freerdp3).
set -euo pipefail
cd "$(dirname "$0")"
spec=$1; shift
name=$(basename "$spec" .spec)
mkdir -p sources out/repo "out/$name"
podman run --rm -v "$PWD:/w:Z" -w /w docker.io/library/almalinux:8 bash -euxc '
  dnf -y -q install epel-release dnf-plugins-core rpm-build rpmdevtools createrepo_c
  dnf config-manager --set-enabled powertools
  createrepo_c -q out/repo
  printf "[local]\nname=local\nbaseurl=file:///w/out/repo\ngpgcheck=0\npriority=1\n" > /etc/yum.repos.d/local.repo
  spectool -g -C sources "$0"
  dnf -y builddep "$0" "$@"
  rpmbuild -ba --define "_sourcedir /w/sources" --define "_topdir /tmp/rb" \
    --define "_rpmdir /w/out/'"$name"'" --define "_srcrpmdir /w/out/'"$name"'" "$0" "$@"
' "$spec" "$@" 2>&1 | tee "out/$name/build.log"
