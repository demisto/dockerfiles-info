# `demisto/pwsh-azure:1.0.0.7410`
## Docker Metadata
- Image Size: `89.66 MB`
- Image ID: `sha256:6903e1a68ec6ce6e952d478b8f84b84074f42c75e7211792a6cda84bd36a0ae3`
- Created: `2020-04-16T09:40:37.258318708Z`
- Arch: `linux`/`amd64`
- Command: `["pwsh"]`
- Environment:
  - `PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin`
  - `PS_INSTALL_FOLDER=/opt/microsoft/powershell/6`
  - `DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=false`
  - `LC_ALL=en_US.UTF-8`
  - `LANG=en_US.UTF-8`
  - `PSModuleAnalysisCachePath=/var/cache/microsoft/powershell/PSModuleAnalysisCache/ModuleAnalysisCache`
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
  - `org.opencontainers.image.revision:ee9a4a709742b00841cbb522151caaa5eb580c8e`
  - `org.opencontainers.image.version:1.0.0.7410`
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

Signatures for demisto/pwsh-azure:1.0.0.7410

SIGNED TAG          DIGEST                                                             SIGNERS
1.0.0.7410          204ddf0918b20ae57966d72d3df50620f122be52adeb272100554a0fcee5fbc5   (Repo Admin)

Administrative keys for demisto/pwsh-azure:1.0.0.7410

  Repository Key:	0759ec1c8bfae89a0a4ae57bde62626fea4ee6ec8273bc72762cdfce85c2b4ba
  Root Key:	18c792726f709f224ce175fd42b0a31ea143df2dc9e5ba0c591cb6d8dc47eaa7

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
