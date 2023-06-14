# MicroPython Winbond Flash

[![Downloads](https://pepy.tech/badge/micropython-winbond)](https://pepy.tech/project/micropython-winbond)
![Release](https://img.shields.io/github/v/release/brainelectronics/micropython-winbond?include_prereleases&color=success)
![MicroPython](https://img.shields.io/badge/micropython-Ok-green.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/brainelectronics/micropython-winbond/actions/workflows/release.yml/badge.svg)](https://github.com/brainelectronics/micropython-winbond/actions/workflows/release.yml)

MicroPython library to interact with Winbond W25Q Flash chips

📚 The latest documentation is available at
[MicroPython Winbond ReadTheDocs][ref-rtd-micropython-winbond] 📚

-----------------------

<!-- MarkdownTOC -->

- [Installation](#installation)
    - [Install required tools](#install-required-tools)
- [Stetup](#stetup)
    - [Install package](#install-package)
        - [General](#general)
        - [Specific version](#specific-version)
        - [Test version](#test-version)
    - [Manually](#manually)
        - [Upload files to board](#upload-files-to-board)
- [Usage](#usage)
- [Credits](#credits)

<!-- /MarkdownTOC -->

## Installation

### Install required tools

Python3 must be installed on your system. Check the current Python version
with the following command

```bash
python --version
python3 --version
```

Depending on which command `Python 3.x.y` (with x.y as some numbers) is
returned, use that command to proceed.

```bash
python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

For interaction with the filesystem of the device the
[Remote MicroPython shell][ref-remote-upy-shell] can be used.

Test the tool by showing its man/help info description.

```bash
rshell --help
```

## Stetup

### Install package

Connect the MicroPython device to a network (if possible)

```python
import network
station = network.WLAN(network.STA_IF)
station.active(True)
station.connect('SSID', 'PASSWORD')
station.isconnected()
```

#### General

Install the latest package version of this lib on the MicroPython device

```python
import mip
mip.install("github:brainelectronics/micropython-winbond")
```

For MicroPython versions below 1.19.1 use the `upip` package instead of `mip`

```python
import upip
upip.install('micropython-winbond')
```

#### Specific version

Install a specific, fixed package version of this lib on the MicroPython device

```python
import mip
# install a verions of a specific branch
mip.install("github:brainelectronics/micropython-winbond", version="feature/add-docs-and-detailed-examples")
# install a tag version
mip.install("github:brainelectronics/micropython-winbond", version="0.4.0")
```

For MicroPython versions below 1.19.1 use the `upip` package instead of `mip`.
With `upip` always the latest available version will be installed.

```python
import upip
upip.install('micropython-winbond')
```

#### Test version

Install a specific release candidate version uploaded to
[Test Python Package Index](https://test.pypi.org/) on every PR on the
MicroPython device. If no specific version is set, the latest stable version
will be used.

```python
import mip
mip.install("github:brainelectronics/micropython-winbond", version="0.4.0-rc2.dev4")
```

For MicroPython versions below 1.19.1 use the `upip` package instead of `mip`.
With `upip` always the latest available version will be installed.

```python
import upip
# overwrite index_urls to only take artifacts from test.pypi.org
upip.index_urls = ['https://test.pypi.org/pypi']
upip.install('micropython-winbond')
```

See also [brainelectronics Test PyPi Server in Docker][ref-brainelectronics-test-pypiserver]
for a test PyPi server running on Docker.

### Manually

#### Upload files to board

Copy the module to the MicroPython board and import them as shown below
using [Remote MicroPython shell][ref-remote-upy-shell]

Open the remote shell with the following command. Additionally use `-b 115200`
in case no CP210x is used but a CH34x.

```bash
rshell -p /dev/tty.SLAB_USBtoUART --editor nano
```

Perform the following command inside the `rshell` to copy all files and
folders to the device

```bash
mkdir /pyboard/lib
mkdir /pyboard/lib/winbond

cp winbond/* /pyboard/lib/winbond
cp main.py /pyboard/lib/winbond
cp boot.py /pyboard/lib/winbond
```

## Usage

```python
from machine import SPI, Pin
import os
from winbond import W25QFlash

# the used SPI and CS pin is setup specific, change accordingly
# check the boot.py file of this repo for further boards
flash = W25QFlash(spi=SPI(2), cs=Pin(5), baud=2000000, software_reset=True)

flash_mount_point = '/external'

try:
    os.mount(flash, flash_mount_point)
except Exception as e:
    if e.errno == 19:
        # [Errno 19] ENODEV aka "No such device"
        # create the filesystem, this takes some seconds (approx. 10 sec)
        print('Creating filesystem for external flash ...')
        print('This might take up to 10 seconds')
        os.VfsFat.mkfs(flash)
    else:
        # takes some seconds/minutes (approx. 40 sec for 128MBit/16MB)
        print('Formatting external flash ...')
        print('This might take up to 60 seconds')
        # !!! only required on the very first start (will remove everything)
        flash.format()

        # create the filesystem, this takes some seconds (approx. 10 sec)
        print('Creating filesystem for external flash ...')
        print('This might take up to 10 seconds')
        # !!! only required on first setup and after formatting
        os.VfsFat.mkfs(flash)

    print('Filesystem for external flash created')

    # finally mount the external flash
    os.mount(flash, flash_mount_point)
```

## Credits

Kudos and big thank you to [crizeo of the MicroPython Forum][ref-crizeo] and
his [post to use Winbond flash chips][ref-upy-forum-winbond-driver]

<!-- Links -->
[ref-rtd-micropython-winbond]: https://micropython-winbond.readthedocs.io/en/latest/
[ref-remote-upy-shell]: https://github.com/dhylands/rshell
[ref-brainelectronics-test-pypiserver]: https://github.com/brainelectronics/test-pypiserver
[ref-crizeo]: https://forum.micropython.org/memberlist.php?mode=viewprofile&u=3067
[ref-upy-forum-winbond-driver]: https://forum.micropython.org/viewtopic.php?f=16&t=3899&start=10
