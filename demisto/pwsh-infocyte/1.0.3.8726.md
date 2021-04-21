# `demisto/pwsh-infocyte:1.0.3.8726`
## Docker Metadata
- Image Size: `61.81 MB`
- Image ID: `sha256:db274cf917ed23e488b143881fc842266d260499d32463fa48d57184a1a9080f`
- Created: `2020-06-01T13:07:24.625816039Z`
- Arch: `linux`/`amd64`
- Command: `["pwsh"]`
- Environment:
  - `PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin`
  - `PS_INSTALL_FOLDER=/opt/microsoft/powershell/6`
  - `DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=false`
  - `LC_ALL=en_US.UTF-8`
  - `LANG=en_US.UTF-8`
  - `PSModuleAnalysisCachePath=/var/cache/microsoft/powershell/PSModuleAnalysisCache/ModuleAnalysisCache`
  - `DOCKER_IMAGE=demisto/pwsh-infocyte:1.0.3.8726`
- Labels:
  - `description:This Dockerfile will install the latest release of PowerShell.`
  - `maintainer:PowerShell Team <powershellteam@hotmail.com>`
  - `org.label-schema.docker.cmd:docker run mcr.microsoft.com/v6.2.4/powershell:6.2.4-alpine-3.8 pwsh -c ''`
  - `org.label-schema.docker.cmd.devel:docker run mcr.microsoft.com/v6.2.4/powershell:6.2.4-alpine-3.8`
  - `org.label-schema.docker.cmd.help:docker run mcr.microsoft.com/v6.2.4/powershell:6.2.4-alpine-3.8 pwsh -c Get-Help`
  - `org.label-schema.docker.cmd.test:docker run mcr.microsoft.com/v6.2.4/powershell:6.2.4-alpine-3.8 pwsh -c Invoke-Pester`
  - `org.label-schema.name:powershell`
  - `org.label-schema.schema-version:1.0`
  - `org.label-schema.url:https://github.com/PowerShell/PowerShell/blob/master/docker/README.md`
  - `org.label-schema.usage:https://github.com/PowerShell/PowerShell/tree/master/docker#run-the-docker-image-you-built`
  - `org.label-schema.vcs-ref:fdaef2d`
  - `org.label-schema.vcs-url:https://github.com/PowerShell/PowerShell-Docker`
  - `org.label-schema.vendor:PowerShell`
  - `org.label-schema.version:6.2.4`
  - `org.opencontainers.image.authors:Demisto <containers@demisto.com>`
  - `org.opencontainers.image.revision:7aabdbd65e7d02fd87014056b534d9ed5d14dc27`
  - `org.opencontainers.image.version:1.0.3.8726`
  - `readme.md:https://github.com/PowerShell/PowerShell/blob/master/docker/README.md`

- OS Release:
  - `NAME="Alpine Linux"`
  - `ID=alpine`
  - `VERSION_ID=3.8.5`
  - `PRETTY_NAME="Alpine Linux v3.8"`
  - `HOME_URL="http://alpinelinux.org"`
  - `BUG_REPORT_URL="http://bugs.alpinelinux.org"`

## Docker Trust
```

Signatures for demisto/pwsh-infocyte:1.0.3.8726

SIGNED TAG          DIGEST                                                             SIGNERS
1.0.3.8726          72449a13e2fed1bc8187969a760304272a5e1f7da0a112a2097d2e4e6c02356a   (Repo Admin)

Administrative keys for demisto/pwsh-infocyte:1.0.3.8726

  Repository Key:	c01ca20df8e20c3307aae9bc588ccc0365064e9d2e2cea0479016eee5f46c274
  Root Key:	3d193ad829fc71df2950ab77fa48ae09cca5a2a45bd82e66c2a1fd3cb8e4dd7a

```

## `Python Packages`


## `OS Packages`

* alpine-baselayout-3.1.0-r0 x86_64 {alpine-baselayout}
* alpine-keys-2.1-r1 x86_64 {alpine-keys}
* apk-tools-2.10.1-r0 x86_64 {apk-tools}
* busybox-1.28.4-r3 x86_64 {busybox}
* ca-certificates-20190108-r0 x86_64 {ca-certificates}
* icu-libs-60.2-r2 x86_64 {icu}
* keyutils-libs-1.5.10-r0 x86_64 {keyutils}
* krb5-conf-1.0-r1 x86_64 {krb5-conf}
* krb5-libs-1.15.4-r0 x86_64 {krb5}
* less-530-r0 x86_64 {less}
* libc-utils-0.7.1-r0 x86_64 {libc-dev}
* libcom_err-1.44.2-r2 x86_64 {e2fsprogs}
* libcrypto1.0-1.0.2u-r0 x86_64 {openssl}
* libgcc-6.4.0-r9 x86_64 {gcc}
* libintl-0.19.8.1-r2 x86_64 {gettext}
* libressl2.7-libcrypto-2.7.5-r0 x86_64 {libressl}
* libressl2.7-libssl-2.7.5-r0 x86_64 {libressl}
* libressl2.7-libtls-2.7.5-r0 x86_64 {libressl}
* libssl1.0-1.0.2u-r0 x86_64 {openssl}
* libstdc++-6.4.0-r9 x86_64 {gcc}
* libverto-0.3.0-r1 x86_64 {libverto}
* lttng-ust-2.10.1-r0 x86_64 {lttng-ust}
* musl-1.1.19-r11 x86_64 {musl}
* musl-utils-1.1.19-r11 x86_64 {musl}
* ncurses-libs-6.1_p20180818-r1 x86_64 {ncurses}
* ncurses-terminfo-6.1_p20180818-r1 x86_64 {ncurses}
* ncurses-terminfo-base-6.1_p20180818-r1 x86_64 {ncurses}
* scanelf-1.2.3-r0 x86_64 {pax-utils}
* ssl_client-1.28.4-r3 x86_64 {busybox}
* tzdata-2019c-r0 x86_64 {tzdata}
* userspace-rcu-0.10.1-r0 x86_64 {userspace-rcu}
* zlib-1.2.11-r1 x86_64 {zlib}
