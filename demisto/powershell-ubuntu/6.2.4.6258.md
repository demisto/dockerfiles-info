# `demisto/powershell-ubuntu:6.2.4.6258`
## Docker Metadata
- Image Size: `110.75 MB`
- Image ID: `sha256:3994f87b4601fc5d3d7f28502ffd5a0b5056bf97e3e932dbdec022e2a19aca1e`
- Created: `2020-02-26T20:15:55.580542202Z`
- Arch: `linux`/`amd64`
- Command: `["pwsh"]`
- Environment:
  - `PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin`
  - `DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=false`
  - `LC_ALL=en_US.UTF-8`
  - `LANG=en_US.UTF-8`
  - `PSModuleAnalysisCachePath=/var/cache/microsoft/powershell/PSModuleAnalysisCache/ModuleAnalysisCache`
- Labels:
  - `description:This Dockerfile will install the latest release of PowerShell.`
  - `maintainer:PowerShell Team <powershellteam@hotmail.com>`
  - `org.label-schema.docker.cmd:docker run mcr.microsoft.com/v6.2.4/powershell:6.2.4-ubuntu-bionic pwsh -c ''`
  - `org.label-schema.docker.cmd.devel:docker run mcr.microsoft.com/v6.2.4/powershell:6.2.4-ubuntu-bionic`
  - `org.label-schema.docker.cmd.help:docker run mcr.microsoft.com/v6.2.4/powershell:6.2.4-ubuntu-bionic pwsh -c Get-Help`
  - `org.label-schema.docker.cmd.test:docker run mcr.microsoft.com/v6.2.4/powershell:6.2.4-ubuntu-bionic pwsh -c Invoke-Pester`
  - `org.label-schema.name:powershell`
  - `org.label-schema.schema-version:1.0`
  - `org.label-schema.url:https://github.com/PowerShell/PowerShell/blob/master/docker/README.md`
  - `org.label-schema.usage:https://github.com/PowerShell/PowerShell/tree/master/docker#run-the-docker-image-you-built`
  - `org.label-schema.vcs-ref:fdaef2d`
  - `org.label-schema.vcs-url:https://github.com/PowerShell/PowerShell-Docker`
  - `org.label-schema.vendor:PowerShell`
  - `org.label-schema.version:6.2.4`
  - `org.opencontainers.image.authors:Demisto <containers@demisto.com>`
  - `org.opencontainers.image.revision:046ed158c302d4f2ec2988256764113f59219aa5`
  - `org.opencontainers.image.version:6.2.4.6258`
  - `readme.md:https://github.com/PowerShell/PowerShell/blob/master/docker/README.md`

- OS Release:
  - `NAME="Ubuntu"`
  - `VERSION="18.04.4 LTS (Bionic Beaver)"`
  - `ID=ubuntu`
  - `ID_LIKE=debian`
  - `PRETTY_NAME="Ubuntu 18.04.4 LTS"`
  - `VERSION_ID="18.04"`
  - `HOME_URL="https://www.ubuntu.com/"`
  - `SUPPORT_URL="https://help.ubuntu.com/"`
  - `BUG_REPORT_URL="https://bugs.launchpad.net/ubuntu/"`
  - `PRIVACY_POLICY_URL="https://www.ubuntu.com/legal/terms-and-policies/privacy-policy"`
  - `VERSION_CODENAME=bionic`
  - `UBUNTU_CODENAME=bionic`

## Docker Trust
```

Signatures for demisto/powershell-ubuntu:6.2.4.6258

SIGNED TAG          DIGEST                                                             SIGNERS
6.2.4.6258          15a2cda3f60a0fa644cf956af8c69522bcb3f94402b611cc763ca5945931cc73   (Repo Admin)

Administrative keys for demisto/powershell-ubuntu:6.2.4.6258

  Repository Key:	9b056fdc7eefc4a718830a1e91a246777af31d6e458a11eac5a241c987aba36c
  Root Key:	ede55c64378a2bc8ae0e4c31b58956b904597dc4c4354bfe26334df45d2e041d

```

## `Python Packages`


## `OS Packages`

* adduser	3.116ubuntu1
* apt	1.6.12
* base-files	10.1ubuntu2.8
* base-passwd	3.5.44
* bash	4.4.18-2ubuntu1.2
* bsdutils	1:2.31.1-0.4ubuntu3.5
* bzip2	1.0.6-8.1ubuntu0.2
* ca-certificates	20180409
* coreutils	8.28-1ubuntu1
* curl	7.58.0-2ubuntu3.8
* dash	0.5.8-2.10
* debconf	1.5.66ubuntu1
* debianutils	4.8.4
* diffutils	1:3.6-1
* dpkg	1.19.0.5ubuntu2.3
* e2fsprogs	1.44.1-1ubuntu1.3
* fdisk	2.31.1-0.4ubuntu3.5
* findutils	4.6.0+git+20170828-2
* gcc-8-base:amd64	8.3.0-6ubuntu1~18.04.1
* gpgv	2.2.4-1ubuntu1.2
* grep	3.1-2build1
* gss-ntlmssp	0.7.0-4build3
* gzip	1.6-5ubuntu1
* hostname	3.20
* init-system-helpers	1.51
* krb5-locales	1.16-2ubuntu0.1
* less	487-0.1
* libacl1:amd64	2.2.52-3build1
* libapt-pkg5.0:amd64	1.6.12
* libasn1-8-heimdal:amd64	7.5.0+dfsg-1
* libattr1:amd64	1:2.4.47-2build1
* libaudit1:amd64	1:2.8.2-1ubuntu1
* libaudit-common	1:2.8.2-1ubuntu1
* libblkid1:amd64	2.31.1-0.4ubuntu3.5
* libbsd0:amd64	0.8.7-1ubuntu0.1
* libbz2-1.0:amd64	1.0.6-8.1ubuntu0.2
* libc6:amd64	2.27-3ubuntu1
* libcap-ng0:amd64	0.7.7-3.1
* libc-bin	2.27-3ubuntu1
* libcom-err2:amd64	1.44.1-1ubuntu1.3
* libcurl4:amd64	7.58.0-2ubuntu3.8
* libdb5.3:amd64	5.3.28-13.1ubuntu1.1
* libdebconfclient0:amd64	0.213ubuntu1
* libext2fs2:amd64	1.44.1-1ubuntu1.3
* libfdisk1:amd64	2.31.1-0.4ubuntu3.5
* libffi6:amd64	3.2.1-8
* libgcc1:amd64	1:8.3.0-6ubuntu1~18.04.1
* libgcrypt20:amd64	1.8.1-4ubuntu1.2
* libgmp10:amd64	2:6.1.2+dfsg-2
* libgnutls30:amd64	3.5.18-1ubuntu1.3
* libgpg-error0:amd64	1.27-6
* libgssapi3-heimdal:amd64	7.5.0+dfsg-1
* libgssapi-krb5-2:amd64	1.16-2ubuntu0.1
* libhcrypto4-heimdal:amd64	7.5.0+dfsg-1
* libheimbase1-heimdal:amd64	7.5.0+dfsg-1
* libheimntlm0-heimdal:amd64	7.5.0+dfsg-1
* libhogweed4:amd64	3.4-1
* libhx509-5-heimdal:amd64	7.5.0+dfsg-1
* libicu60:amd64	60.2-3ubuntu3
* libidn2-0:amd64	2.0.4-1.1ubuntu0.2
* libk5crypto3:amd64	1.16-2ubuntu0.1
* libkeyutils1:amd64	1.5.9-9.2ubuntu2
* libkrb5-26-heimdal:amd64	7.5.0+dfsg-1
* libkrb5-3:amd64	1.16-2ubuntu0.1
* libkrb5support0:amd64	1.16-2ubuntu0.1
* libldap-2.4-2:amd64	2.4.45+dfsg-1ubuntu1.4
* libldap-common	2.4.45+dfsg-1ubuntu1.4
* liblttng-ust0:amd64	2.10.1-1
* liblttng-ust-ctl4:amd64	2.10.1-1
* liblz4-1:amd64	0.0~r131-2ubuntu3
* liblzma5:amd64	5.2.2-1.3
* libmount1:amd64	2.31.1-0.4ubuntu3.5
* libncurses5:amd64	6.1-1ubuntu1.18.04
* libncursesw5:amd64	6.1-1ubuntu1.18.04
* libnettle6:amd64	3.4-1
* libnghttp2-14:amd64	1.30.0-1ubuntu1
* libp11-kit0:amd64	0.23.9-2
* libpam0g:amd64	1.1.8-3.6ubuntu2.18.04.1
* libpam-modules:amd64	1.1.8-3.6ubuntu2.18.04.1
* libpam-modules-bin	1.1.8-3.6ubuntu2.18.04.1
* libpam-runtime	1.1.8-3.6ubuntu2.18.04.1
* libpcre3:amd64	2:8.39-9
* libprocps6:amd64	2:3.3.12-3ubuntu1.2
* libpsl5:amd64	0.19.1-5build1
* libroken18-heimdal:amd64	7.5.0+dfsg-1
* librtmp1:amd64	2.4+20151223.gitfa8646d.1-1
* libsasl2-2:amd64	2.1.27~101-g0780600+dfsg-3ubuntu2.1
* libsasl2-modules:amd64	2.1.27~101-g0780600+dfsg-3ubuntu2.1
* libsasl2-modules-db:amd64	2.1.27~101-g0780600+dfsg-3ubuntu2.1
* libseccomp2:amd64	2.4.1-0ubuntu0.18.04.2
* libselinux1:amd64	2.7-2build2
* libsemanage1:amd64	2.7-2build2
* libsemanage-common	2.7-2build2
* libsepol1:amd64	2.7-1
* libsmartcols1:amd64	2.31.1-0.4ubuntu3.5
* libsqlite3-0:amd64	3.22.0-1ubuntu0.2
* libss2:amd64	1.44.1-1ubuntu1.3
* libssl1.0.0:amd64	1.0.2n-1ubuntu5.3
* libssl1.1:amd64	1.1.1-1ubuntu2.1~18.04.5
* libstdc++6:amd64	8.3.0-6ubuntu1~18.04.1
* libsystemd0:amd64	237-3ubuntu10.39
* libtasn1-6:amd64	4.13-2
* libtinfo5:amd64	6.1-1ubuntu1.18.04
* libudev1:amd64	237-3ubuntu10.39
* libunistring2:amd64	0.9.9-0ubuntu2
* liburcu6:amd64	0.10.1-1
* libuuid1:amd64	2.31.1-0.4ubuntu3.5
* libwbclient0:amd64	2:4.7.6+dfsg~ubuntu-0ubuntu2.15
* libwind0-heimdal:amd64	7.5.0+dfsg-1
* libzstd1:amd64	1.3.3+dfsg-2ubuntu1.1
* locales	2.27-3ubuntu1
* login	1:4.5-1ubuntu2
* lsb-base	9.20170808ubuntu1
* mawk	1.3.3-17ubuntu3
* mount	2.31.1-0.4ubuntu3.5
* ncurses-base	6.1-1ubuntu1.18.04
* ncurses-bin	6.1-1ubuntu1.18.04
* openssl	1.1.1-1ubuntu2.1~18.04.5
* passwd	1:4.5-1ubuntu2
* perl-base	5.26.1-6ubuntu0.3
* powershell	6.2.4-1.ubuntu.18.04
* procps	2:3.3.12-3ubuntu1.2
* publicsuffix	20180223.1310-1
* sed	4.4-2
* sensible-utils	0.0.12
* sysvinit-utils	2.88dsf-59.10ubuntu1
* tar	1.29b-2ubuntu0.1
* ubuntu-keyring	2018.09.18.1~18.04.0
* util-linux	2.31.1-0.4ubuntu3.5
* zlib1g:amd64	1:1.2.11.dfsg-0ubuntu2
