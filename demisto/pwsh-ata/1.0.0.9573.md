# `demisto/pwsh-ata:1.0.0.9573`
## Docker Metadata
- Image Size: `63.89 MB`
- Image ID: `sha256:187db9ff8e53bce09a070fd4cee6a098b4f2be0d624be085b84618fb3202c0ca`
- Created: `2020-06-23T11:00:36.838234769Z`
- Arch: `linux`/`amd64`
- Command: `["pwsh"]`
- Environment:
  - `PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin`
  - `PS_INSTALL_FOLDER=/opt/microsoft/powershell/7`
  - `DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=false`
  - `LC_ALL=en_US.UTF-8`
  - `LANG=en_US.UTF-8`
  - `PSModuleAnalysisCachePath=/var/cache/microsoft/powershell/PSModuleAnalysisCache/ModuleAnalysisCache`
  - `POWERSHELL_DISTRIBUTION_CHANNEL=PSDocker-Alpine-3.10`
  - `DOCKER_IMAGE=demisto/pwsh-ata:1.0.0.9573`
- Labels:
  - `description:This Dockerfile will install the latest release of PowerShell.`
  - `maintainer:PowerShell Team <powershellteam@hotmail.com>`
  - `org.label-schema.docker.cmd:docker run mcr.microsoft.com/v7.0.1/powershell:7.0.1-alpine-3.10 pwsh -c ''`
  - `org.label-schema.docker.cmd.devel:docker run mcr.microsoft.com/v7.0.1/powershell:7.0.1-alpine-3.10`
  - `org.label-schema.docker.cmd.help:docker run mcr.microsoft.com/v7.0.1/powershell:7.0.1-alpine-3.10 pwsh -c Get-Help`
  - `org.label-schema.docker.cmd.test:docker run mcr.microsoft.com/v7.0.1/powershell:7.0.1-alpine-3.10 pwsh -c Invoke-Pester`
  - `org.label-schema.name:powershell`
  - `org.label-schema.schema-version:1.0`
  - `org.label-schema.url:https://github.com/PowerShell/PowerShell/blob/master/docker/README.md`
  - `org.label-schema.usage:https://github.com/PowerShell/PowerShell/tree/master/docker#run-the-docker-image-you-built`
  - `org.label-schema.vcs-ref:7d20d98`
  - `org.label-schema.vcs-url:https://github.com/PowerShell/PowerShell-Docker`
  - `org.label-schema.vendor:PowerShell`
  - `org.label-schema.version:7.0.1`
  - `org.opencontainers.image.authors:Demisto <containers@demisto.com>`
  - `org.opencontainers.image.revision:bc3db7620c216d6ac4ef9104c00283382fc380fc`
  - `org.opencontainers.image.version:1.0.0.9573`
  - `readme.md:https://github.com/PowerShell/PowerShell/blob/master/docker/README.md`

- OS Release:
  - `NAME="Alpine Linux"`
  - `ID=alpine`
  - `VERSION_ID=3.10.5`
  - `PRETTY_NAME="Alpine Linux v3.10"`
  - `HOME_URL="https://alpinelinux.org/"`
  - `BUG_REPORT_URL="https://bugs.alpinelinux.org/"`

## Docker Trust
```

Signatures for demisto/pwsh-ata:1.0.0.9573

SIGNED TAG          DIGEST                                                             SIGNERS
1.0.0.9573          81bd06d2810e4113feb7c99f3989efd5bd4388b7db031ae793486a8654ae9e6e   (Repo Admin)

Administrative keys for demisto/pwsh-ata:1.0.0.9573

  Repository Key:	0ca316557311c84da0dcdad3ff666cc1514aee2fed0ab8d369d67469775bbe44
  Root Key:	8d75f43f600e6495245357c4ad771231eac8f12e3b2e8a52e043ae34b96ad7cf

```

## `Python Packages`


## `OS Packages`

* alpine-baselayout-3.1.2-r0 x86_64 {alpine-baselayout}
* alpine-keys-2.1-r2 x86_64 {alpine-keys}
* apk-tools-2.10.4-r2 x86_64 {apk-tools}
* busybox-1.30.1-r3 x86_64 {busybox}
* ca-certificates-20191127-r0 x86_64 {ca-certificates}
* ca-certificates-cacert-20191127-r0 x86_64 {ca-certificates}
* icu-libs-64.2-r1 x86_64 {icu}
* keyutils-libs-1.6-r1 x86_64 {keyutils}
* krb5-conf-1.0-r1 x86_64 {krb5-conf}
* krb5-libs-1.17-r0 x86_64 {krb5}
* less-551-r0 x86_64 {less}
* libc-utils-0.7.1-r0 x86_64 {libc-dev}
* libcom_err-1.45.5-r0 x86_64 {e2fsprogs}
* libcrypto1.1-1.1.1g-r0 x86_64 {openssl}
* libgcc-8.3.0-r0 x86_64 {gcc}
* libintl-0.19.8.1-r4 x86_64 {gettext}
* libssl1.1-1.1.1g-r0 x86_64 {openssl}
* libstdc++-8.3.0-r0 x86_64 {gcc}
* libtls-standalone-2.9.1-r0 x86_64 {libtls-standalone}
* libverto-0.3.1-r0 x86_64 {libverto}
* lttng-ust-2.10.3-r0 x86_64 {lttng-ust}
* musl-1.1.22-r3 x86_64 {musl}
* musl-utils-1.1.22-r3 x86_64 {musl}
* ncurses-libs-6.1_p20190518-r2 x86_64 {ncurses}
* ncurses-terminfo-base-6.1_p20190518-r2 x86_64 {ncurses}
* scanelf-1.2.3-r0 x86_64 {pax-utils}
* ssl_client-1.30.1-r3 x86_64 {busybox}
* tzdata-2020a-r0 x86_64 {tzdata}
* userspace-rcu-0.11.0-r0 x86_64 {userspace-rcu}
* zlib-1.2.11-r1 x86_64 {zlib}
