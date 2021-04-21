# `demisto/powershell-core:6.2.1.1896`

## Docker Metadata
- Image ID: `sha256:f89ac33e3e606010b3afa04c1034a6744a5e9dadc386348f9c47e16247c4f244`
- Created: `2019-09-18T13:24:00.753687362Z`
- Arch: `linux`/`amd64`
- Command: `["python"]`
- Environment:
  - `PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin`
  - `PS_INSTALL_FOLDER=/opt/microsoft/powershell/6`
  - `DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=false`
  - `LC_ALL=en_US.UTF-8`
  - `LANG=C.UTF-8`
  - `PSModuleAnalysisCachePath=/var/cache/microsoft/powershell/PSModuleAnalysisCache/ModuleAnalysisCache`
  - `PYTHONIOENCODING=UTF-8`
  - `GPG_KEY=C01E1CAD5EA2C4F0B8E3571504C367C218ADD4FF`
  - `PYTHON_VERSION=2.7.16`
  - `PYTHON_PIP_VERSION=19.0.3`
- Labels:
  - `description:This Dockerfile will install the latest release of PowerShell.`
  - `maintainer:PowerShell Team <powershellteam@hotmail.com>`
  - `org.label-schema.docker.cmd:docker run mcr.microsoft.com/v6.2.1/powershell:6.2.1-alpine-3.8 pwsh -c ''`
  - `org.label-schema.docker.cmd.devel:docker run mcr.microsoft.com/v6.2.1/powershell:6.2.1-alpine-3.8`
  - `org.label-schema.docker.cmd.help:docker run mcr.microsoft.com/v6.2.1/powershell:6.2.1-alpine-3.8 pwsh -c Get-Help`
  - `org.label-schema.docker.cmd.test:docker run mcr.microsoft.com/v6.2.1/powershell:6.2.1-alpine-3.8 pwsh -c Invoke-Pester`
  - `org.label-schema.name:powershell`
  - `org.label-schema.schema-version:1.0`
  - `org.label-schema.url:https://github.com/PowerShell/PowerShell/blob/master/docker/README.md`
  - `org.label-schema.usage:https://github.com/PowerShell/PowerShell/tree/master/docker#run-the-docker-image-you-built`
  - `org.label-schema.vcs-ref:6cb3eb5`
  - `org.label-schema.vcs-url:https://github.com/PowerShell/PowerShell-Docker`
  - `org.label-schema.vendor:PowerShell`
  - `org.label-schema.version:6.2.1`
  - `org.opencontainers.image.authors:Demisto <containers@demisto.com>`
  - `org.opencontainers.image.revision:030d2b662e84c884e96323f812ca9ae48b0bed15`
  - `org.opencontainers.image.version:6.2.1.1896`
  - `readme.md:https://github.com/PowerShell/PowerShell/blob/master/docker/README.md`


## `Python Packages`


### `certifi`

* Summary: Python package for providing Mozilla's CA Bundle.
* Version: 2019.9.11
* Pypi: https://pypi.org/project/certifi/
* Homepage: https://certifi.io/
* Author: Kenneth Reitz me@kennethreitz.com
* License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)

### `chardet`

* Summary: Universal encoding detector for Python 2 and 3
* Version: 3.0.4
* Pypi: https://pypi.org/project/chardet/
* Homepage: https://github.com/chardet/chardet
* Author: Daniel Blanchard dan.blanchard@gmail.com
* License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)

### `dateparser`

* Summary: Date parsing library designed to parse dates from HTML pages
* Version: 0.7.2
* Pypi: https://pypi.org/project/dateparser/
* Homepage: https://github.com/scrapinghub/dateparser
* Author: Scrapinghub info@scrapinghub.com
* License :: OSI Approved :: BSD License

### `idna`

* Summary: Internationalized Domain Names in Applications (IDNA)
* Version: 2.8
* Pypi: https://pypi.org/project/idna/
* Homepage: https://github.com/kjd/idna
* Author: Kim Davies kim@cynosure.com.au
* License :: OSI Approved :: BSD License

### `olefile`

* Summary: Python package to parse, read and write Microsoft OLE2 files (Structured Storage or Compound Document, Microsoft Office)
* Version: 0.46
* Pypi: https://pypi.org/project/olefile/
* Homepage: https://www.decalage.info/python/olefileio
* Author: Philippe Lagadec nospam@decalage.info
* License :: OSI Approved :: BSD License

### `pip`

* Summary: The PyPA recommended tool for installing Python packages.
* Version: 19.2.3
* Pypi: https://pypi.org/project/pip/
* Homepage: https://pip.pypa.io/
* Author: The pip developers pypa-dev@groups.google.com
* License :: OSI Approved :: MIT License

### `python-dateutil`

* Summary: Extensions to the standard Python datetime module
* Version: 2.8.0
* Pypi: https://pypi.org/project/python-dateutil/
* Homepage: https://dateutil.readthedocs.io
* Author: Gustavo Niemeyer gustavo@niemeyer.net
* License :: OSI Approved :: Apache Software License
* License :: OSI Approved :: BSD License

### `pytz`

* Summary: World timezone definitions, modern and historical
* Version: 2019.2
* Pypi: https://pypi.org/project/pytz/
* Homepage: http://pythonhosted.org/pytz
* Author: Stuart Bishop stuart@stuartbishop.net
* License :: OSI Approved :: MIT License

### `PyYAML`

* Summary: YAML parser and emitter for Python
* Version: 5.1.2
* Pypi: https://pypi.org/project/PyYAML/
* Homepage: https://github.com/yaml/pyyaml
* Author: Kirill Simonov xi@resolvent.net
* License :: OSI Approved :: MIT License

### `regex`

* Summary: Alternative regular expression module, to replace re.
* Version: 2019.8.19
* Pypi: https://pypi.org/project/regex/
* Homepage: https://bitbucket.org/mrabarnett/mrab-regex
* Author: Matthew Barnett regex@mrabarnett.plus.com
* License :: OSI Approved :: Python Software Foundation License

### `requests`

* Summary: Python HTTP for Humans.
* Version: 2.22.0
* Pypi: https://pypi.org/project/requests/
* Homepage: http://python-requests.org
* Author: Kenneth Reitz me@kennethreitz.org
* License :: OSI Approved :: Apache Software License

### `setuptools`

* Summary: Easily download, build, install, upgrade, and uninstall Python packages
* Version: 41.2.0
* Pypi: https://pypi.org/project/setuptools/
* Homepage: https://github.com/pypa/setuptools
* Author: Python Packaging Authority distutils-sig@python.org
* License :: OSI Approved :: MIT License

### `six`

* Summary: Python 2 and 3 compatibility utilities
* Version: 1.12.0
* Pypi: https://pypi.org/project/six/
* Homepage: https://github.com/benjaminp/six
* Author: Benjamin Peterson benjamin@python.org
* License :: OSI Approved :: MIT License

### `tzlocal`

* Summary: tzinfo object for the local timezone
* Version: 2.0.0
* Pypi: https://pypi.org/project/tzlocal/
* Homepage: https://github.com/regebro/tzlocal
* Author: Lennart Regebro regebro@gmail.com
* License :: OSI Approved :: MIT License

### `urllib3`

* Summary: HTTP library with thread-safe connection pooling, file post, and more.
* Version: 1.25.3
* Pypi: https://pypi.org/project/urllib3/
* Homepage: https://urllib3.readthedocs.io/
* Author: Andrey Petrov andrey.petrov@shazow.net
* License :: OSI Approved :: MIT License

### `wheel`

* Summary: A built-package format for Python.
* Version: 0.33.6
* Pypi: https://pypi.org/project/wheel/
* Homepage: https://github.com/pypa/wheel
* Author: Daniel Holth dholth@fastmail.fm
* License :: OSI Approved :: MIT License

## `OS Packages`

* .python-rundeps-0 noarch {.python-rundeps}
* alpine-baselayout-3.1.0-r0 x86_64 {alpine-baselayout}
* alpine-keys-2.1-r1 x86_64 {alpine-keys}
* apk-tools-2.10.1-r0 x86_64 {apk-tools}
* busybox-1.28.4-r3 x86_64 {busybox}
* ca-certificates-20190108-r0 x86_64 {ca-certificates}
* expat-2.2.7-r1 x86_64 {expat}
* gdbm-1.13-r1 x86_64 {gdbm}
* icu-libs-60.2-r2 x86_64 {icu}
* keyutils-libs-1.5.10-r0 x86_64 {keyutils}
* krb5-conf-1.0-r1 x86_64 {krb5-conf}
* krb5-libs-1.15.4-r0 x86_64 {krb5}
* less-530-r0 x86_64 {less}
* libbz2-1.0.6-r7 x86_64 {bzip2}
* libc-utils-0.7.1-r0 x86_64 {libc-dev}
* libcom_err-1.44.2-r0 x86_64 {e2fsprogs}
* libcrypto1.0-1.0.2t-r0 x86_64 {openssl}
* libffi-3.2.1-r4 x86_64 {libffi}
* libgcc-6.4.0-r9 x86_64 {gcc}
* libintl-0.19.8.1-r2 x86_64 {gettext}
* libnsl-1.0.5-r2 x86_64 {libnsl}
* libressl2.7-libcrypto-2.7.5-r0 x86_64 {libressl}
* libressl2.7-libssl-2.7.5-r0 x86_64 {libressl}
* libressl2.7-libtls-2.7.5-r0 x86_64 {libressl}
* libssl1.0-1.0.2t-r0 x86_64 {openssl}
* libstdc++-6.4.0-r9 x86_64 {gcc}
* libtirpc-1.0.3-r0 x86_64 {libtirpc}
* libverto-0.3.0-r1 x86_64 {libverto}
* lttng-ust-2.10.1-r0 x86_64 {lttng-ust}
* musl-1.1.19-r11 x86_64 {musl}
* musl-utils-1.1.19-r11 x86_64 {musl}
* ncurses-libs-6.1_p20180818-r1 x86_64 {ncurses}
* ncurses-terminfo-6.1_p20180818-r1 x86_64 {ncurses}
* ncurses-terminfo-base-6.1_p20180818-r1 x86_64 {ncurses}
* readline-7.0.003-r0 x86_64 {readline}
* scanelf-1.2.3-r0 x86_64 {pax-utils}
* sqlite-libs-3.25.3-r1 x86_64 {sqlite}
* ssl_client-1.28.4-r3 x86_64 {busybox}
* tzdata-2019a-r0 x86_64 {tzdata}
* userspace-rcu-0.10.1-r0 x86_64 {userspace-rcu}
* zlib-1.2.11-r1 x86_64 {zlib}
