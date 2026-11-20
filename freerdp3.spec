# FreeRDP 3 for EL8, installable alongside RHEL 8's FreeRDP 2 (freerdp,
# freerdp-libs, libwinpr). Derived from Fedora's freerdp.spec.
#
# - Package names carry a "3" (freerdp3, freerdp3-libs, libwinpr3, ...) and
#   binaries are versioned (xfreerdp3, wlfreerdp3, winpr-makecert3, ...).
# - uwac is linked statically (libuwac0 belongs to FreeRDP 2 on EL8).
# - H.264: built against OpenH264's API headers only and loads libopenh264
#   at runtime. Run freerdp3-install-openh264 to fetch Cisco's licensed
#   binary. No H.264 implementation is shipped here.

%undefine __cmake_in_source_build

Name:           freerdp3
Version:        3.33.1
Release:        1%{?dist}
Summary:        Free implementation of the Remote Desktop Protocol (RDP), version 3

License:        Apache-2.0 AND HPND AND LGPL-2.1-or-later AND LicenseRef-Fedora-Public-Domain AND BSD-2-Clause
URL:            https://www.freerdp.com/
Source0:        https://github.com/FreeRDP/FreeRDP/releases/download/%{version}/freerdp-%{version}.tar.gz
# OpenH264 public API headers (BSD-2-Clause), from cisco/openh264 v2.7.0
# codec/api/wels/. Headers only; used to dlopen Cisco's binary at runtime.
Source1:        openh264-codec_api.h
Source2:        openh264-codec_app_def.h
Source3:        openh264-codec_def.h
Source4:        openh264-codec_ver.h
Source5:        openh264-LICENSE
Source6:        freerdp3-install-openh264

BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  alsa-lib-devel
BuildRequires:  cmake >= 3.13
BuildRequires:  cups-devel
BuildRequires:  gsm-devel
BuildRequires:  lame-devel
BuildRequires:  libicu-devel
BuildRequires:  libjpeg-turbo-devel
BuildRequires:  turbojpeg-devel
BuildRequires:  libX11-devel
BuildRequires:  libXcursor-devel
BuildRequires:  libXdamage-devel
BuildRequires:  libXext-devel
BuildRequires:  libXi-devel
BuildRequires:  libXinerama-devel
BuildRequires:  libxkbfile-devel
BuildRequires:  libXrandr-devel
BuildRequires:  libXrender-devel
BuildRequires:  libXtst-devel
BuildRequires:  libXv-devel
BuildRequires:  pam-devel
BuildRequires:  python3-devel
BuildRequires:  zlib-devel
BuildRequires:  json-c-devel
BuildRequires:  uriparser-devel
BuildRequires:  pkgconfig(cairo)
BuildRequires:  pkgconfig(krb5)
BuildRequires:  pkgconfig(fuse3)
BuildRequires:  pkgconfig(libcbor)
BuildRequires:  pkgconfig(libfido2)
BuildRequires:  pkgconfig(libpcsclite)
BuildRequires:  pkgconfig(libpulse)
BuildRequires:  pkgconfig(libsystemd)
BuildRequires:  pkgconfig(libusb-1.0)
BuildRequires:  pkgconfig(libwebp)
BuildRequires:  pkgconfig(openssl)
BuildRequires:  pkgconfig(opus)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-scanner)
BuildRequires:  pkgconfig(xkbcommon)

Requires:       %{name}-libs%{?_isa} = %{version}-%{release}
Requires:       libwinpr3%{?_isa} = %{version}-%{release}
Requires:       python3
Requires:       xdg-utils
Requires:       desktop-file-utils

%description
The xfreerdp3 and wlfreerdp3 Remote Desktop Protocol (RDP) clients from the
FreeRDP 3 project, packaged to coexist with the system FreeRDP 2.

%package        libs
Summary:        Core libraries implementing the RDP protocol (FreeRDP 3)
Requires:       libwinpr3%{?_isa} = %{version}-%{release}
# for freerdp3-install-openh264
Requires:       bzip2
Requires:       curl

%description    libs
FreeRDP 3 core libraries (libfreerdp3, libfreerdp-client3, channels).

H.264 (RDP GFX AVC420/AVC444) decoding uses OpenH264, loaded at runtime. Run
freerdp3-install-openh264 as root to install Cisco's prebuilt binary.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}-libs%{?_isa} = %{version}-%{release}
Requires:       libwinpr3-devel%{?_isa} = %{version}-%{release}
Requires:       pkgconfig
Requires:       cmake >= 3.13

%description    devel
Libraries and header files for developing applications that use FreeRDP 3.

%package        server
Summary:        Server support for %{name}
Requires:       libwinpr3%{?_isa} = %{version}-%{release}
Requires:       %{name}-libs%{?_isa} = %{version}-%{release}

%description    server
FreeRDP 3 servers (freerdp-proxy3, freerdp-shadow-cli3).

%package -n     libwinpr3
Summary:        Windows Portable Runtime (FreeRDP 3)

%description -n libwinpr3
WinPR 3 provides Windows API compatibility for FreeRDP 3.

%package -n     libwinpr3-devel
Summary:        Windows Portable Runtime development files (FreeRDP 3)
Requires:       libwinpr3%{?_isa} = %{version}-%{release}
Requires:       pkgconfig
Requires:       cmake >= 3.13

%description -n libwinpr3-devel
Libraries and header files for developing applications that use WinPR 3.

%prep
%autosetup -p1 -n freerdp-%{version}
mkdir -p openh264/include/wels
for h in codec_api codec_app_def codec_def codec_ver; do
    cp -p %{_sourcedir}/openh264-$h.h openh264/include/wels/$h.h
done
cp -p %{SOURCE5} LICENSE.openh264-headers

%py3_shebang_fix client/common/xdg-aad-helper/xdg-aad-helper.py client/common/xdg-aad-helper/freerdp_aad_handler.py

%build
%cmake \
    -DBUILD_TESTING=OFF \
    -DCMAKE_INSTALL_LIBDIR:PATH=%{_lib} \
    -DCMAKE_SKIP_INSTALL_RPATH=ON \
    -DWITH_BINARY_VERSIONING=ON \
    -DWITH_ALSA=ON \
    -DWITH_AAD=ON \
    -DWITH_CAIRO=ON \
    -DWITH_CUPS=ON \
    -DWITH_CHANNELS=ON \
    -DWITH_CLIENT=ON \
    -DWITH_CLIENT_SDL=OFF \
    -DWITH_DSP_FFMPEG=OFF \
    -DWITH_FDK_AAC=OFF \
    -DWITH_FFMPEG=OFF \
    -DWITH_FUSE=ON \
    -DWITH_GSM=ON \
    -DWITH_GFX_AV1=OFF \
    -DWITH_IPP=OFF \
    -DWITH_JPEG=ON \
    -DWITH_JSONC_REQUIRED=ON \
    -DWITH_KEYBOARD_LAYOUT_FROM_FILE=ON \
    -DWITH_KRB5=ON \
    -DWITH_LAME=ON \
    -DWITH_MANPAGES=ON \
    -DWITH_OPENCL=OFF \
    -DWITH_OPENH264=ON \
    -DWITH_OPENH264_LOADING=ON \
    -DOPENH264_INCLUDE_DIR=$PWD/openh264/include \
    -DOPENH264_LIBRARY=openh264-loaded-at-runtime \
    -DWITH_OPENSSL=ON \
    -DWITH_OPUS=ON \
    -DWITH_PCSC=ON \
    -DWITH_PKCS11=ON \
    -DWITH_PULSE=ON \
    -DWITH_RDTK=ON \
    -DWITH_SAMPLE=OFF \
    -DWITH_SERVER=ON \
    -DWITH_SERVER_INTERFACE=ON \
    -DWITH_SHADOW_X11=ON \
    -DWITH_SOXR=OFF \
    -DWITH_SSO_MIB=OFF \
    -DWITH_SWSCALE=OFF \
    -DWITH_TIMEZONE_COMPILED=OFF \
    -DWITH_TIMEZONE_FROM_FILE=ON \
    -DWITH_URIPARSER=ON \
    -DWITH_VERBOSE_WINPR_ASSERT=OFF \
    -DWITH_VIDEO_FFMPEG=OFF \
    -DWITH_WAYLAND=ON \
    -DWITH_X11=ON \
    -DWITH_XCURSOR=ON \
    -DWITH_XDG_AAD_AUTH_HELPER=ON \
    -DWITH_XEXT=ON \
    -DWITH_XKBFILE=ON \
    -DWITH_XI=ON \
    -DWITH_XINERAMA=ON \
    -DWITH_XRENDER=ON \
    -DWITH_XTEST=ON \
    -DWITH_XV=ON \
    -DWITH_ZLIB=ON \
    -DWITH_SSE2=ON \
    -DUWAC_FORCE_STATIC_BUILD=ON \
    -DWINPR_UTILS_IMAGE_PNG=ON \
    -DWINPR_UTILS_IMAGE_WEBP=ON \
    -DWINPR_UTILS_IMAGE_JPEG=ON
%cmake_build

%install
%cmake_install
find %{buildroot} -name "*.a" -delete
install -Dpm 0755 %{SOURCE6} %{buildroot}%{_bindir}/freerdp3-install-openh264

%files
%{_bindir}/winpr-hash3
%{_bindir}/winpr-makecert3
%{_bindir}/wlfreerdp3
%{_bindir}/xfreerdp3
%{_libexecdir}/freerdp-aad-handler
%{_libexecdir}/freerdp-xdg-aad-helper
%{_mandir}/man1/winpr-hash3.1*
%{_mandir}/man1/winpr-makecert3.1*
%{_mandir}/man1/wlfreerdp3.1*
%{_mandir}/man1/xfreerdp3.1*

%files libs
%license LICENSE LICENSE.openh264-headers
%doc README.md ChangeLog
%{_bindir}/freerdp3-install-openh264
%{_datadir}/FreeRDP/
%{_libdir}/freerdp3/
%{_libdir}/libfreerdp-client3.so.*
%{_libdir}/libfreerdp-server3.so.*
%{_libdir}/libfreerdp-server-proxy3.so.*
%{_libdir}/libfreerdp-shadow3.so.*
%{_libdir}/libfreerdp-shadow-subsystem3.so.*
%{_libdir}/libfreerdp3.so.*
%{_libdir}/librdtk0.so.*
%{_mandir}/man7/freerdp3.7*
%{_mandir}/man7/wlog3.7*

%files devel
%{_includedir}/freerdp3/
%{_includedir}/rdtk0/
%{_libdir}/cmake/FreeRDP3/
%{_libdir}/cmake/FreeRDP-Client3/
%{_libdir}/cmake/FreeRDP-Proxy3/
%{_libdir}/cmake/FreeRDP-Server3/
%{_libdir}/cmake/FreeRDP-Shadow3/
%{_libdir}/cmake/rdtk0/
%{_libdir}/libfreerdp-client3.so
%{_libdir}/libfreerdp-server3.so
%{_libdir}/libfreerdp-server-proxy3.so
%{_libdir}/libfreerdp-shadow3.so
%{_libdir}/libfreerdp-shadow-subsystem3.so
%{_libdir}/libfreerdp3.so
%{_libdir}/librdtk0.so
%{_libdir}/pkgconfig/freerdp3.pc
%{_libdir}/pkgconfig/freerdp-client3.pc
%{_libdir}/pkgconfig/freerdp-server3.pc
%{_libdir}/pkgconfig/freerdp-server-proxy3.pc
%{_libdir}/pkgconfig/freerdp-shadow3.pc
%{_libdir}/pkgconfig/rdtk0.pc

%files server
%{_bindir}/freerdp-proxy3
%{_bindir}/freerdp-shadow-cli3
%{_mandir}/man1/freerdp-proxy3.1*
%{_mandir}/man1/freerdp-shadow-cli3.1*

%files -n libwinpr3
%license LICENSE
%{_datadir}/WinPR/
%{_libdir}/libwinpr3.so.*
%{_libdir}/libwinpr-tools3.so.*

%files -n libwinpr3-devel
%{_libdir}/cmake/WinPR3/
%{_libdir}/cmake/WinPR-tools3/
%{_includedir}/winpr3/
%{_libdir}/libwinpr3.so
%{_libdir}/libwinpr-tools3.so
%{_libdir}/pkgconfig/winpr3.pc
%{_libdir}/pkgconfig/winpr-tools3.pc

%changelog
* Fri Nov 20 2026 remmina-el8 COPR <noreply@localhost> - 3.33.1-1
- FreeRDP 3.33.1 for EL8, parallel-installable with RHEL 8's FreeRDP 2.
- OpenH264 loaded at runtime; freerdp3-install-openh264 fetches Cisco's binary.
