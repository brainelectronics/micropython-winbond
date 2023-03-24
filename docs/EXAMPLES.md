# Examples

Usage examples of this `micropython-winbond` library

---------------

## General

An example of all implemented functionalities can be found at the
[MicroPython Winbond boot and main files][ref-micropython-winbond-root]

## Setup Flash

```python
from machine import SPI, Pin
from winbond import W25QFlash

# the pins and SPI bus can be different on each board
#
# check MicroPython SPI documentation
# https://docs.micropython.org/en/latest/library/machine.SPI.html
# for Device/Port specific setup
# check the docs of your device for further details and pin infos
CS_PIN = Pin(5)
spi = SPI(0)

flash = W25QFlash(spi=spi, cs=CS_PIN, baud=2000000, software_reset=True)
# manufacturer: 0xef
# mem_type: 64
# device: 0x4016
# capacity: 4194304 bytes
```

## Format Flash

```{note}
The flash has to be formated once as an initial step. This step is not
required again. Depending on the flash chip size this might take up to 60
seconds.
```

```python
import os

# create filesystem on the flash chip, approx. 10 sec
os.VfsFat.mkfs(flash)

# format and erase the flash chip content, approx. 40 sec for 128MBit/16MB
flash.format()
```

## Mount Flash

```python
flash_mount_point = '/external'

os.mount(flash, flash_mount_point)
```

```{note}
The flash has to be formated once as an initial step, an
`OSError: [Errno 19] ENODEV` will be thrown otherwise. Refer to the
`Format Flash` section above.
```

## Identify Flash

Identify the flash chip manufacturer, device ID and device capacity in bytes.

```python
flash.identify()
# manufacturer: 0xef
# mem_type: 64
# device: 0x4016
# capacity: 4194304 bytes
```

## Example files

The `boot.py` code will perform the following steps:

 * create a flash object on the SPI bus with a bus speed of 2MHz, chip select
   on machine `pin x` and a software reset interface. Check the datasheet of
   your flash chip whether software reset is supported.
 * try to mount the external flash to `/external`
 	 * in case of `OSError 19` the filesystem will be created first
 	 * otherwise the complete flash will be erased and the filesystem created
 	 * finally mount the external flash

The initial steps of formatting the flash and creating the filesystem will
take around 45 seconds on a 128MBit (16MB) Winbond flash.

The `main.py` code will perform the following steps:

 * list all files and folders on the boards root directory
 * try to read a file named `some-file.txt` on the external flash
 	 * if the file does not exist, it will be created
 * extend the content of `some-file.txt` on the external flash with new content
 * list all files and folders on the external flash directory

A successful output of a first run after a soft reboot should look similar to
this

```
MPY: soft reboot
manufacturer: 0xef
mem_type: 64
device: 0x4018
capacity: 16777216 bytes
Mounting the external flash to "/external" ...
Failed to mount the external flash due to: [Errno 19] ENODEV
Creating filesystem for external flash ...
This might take up to 10 seconds
Filesystem for external flash created
External flash mounted to "/external"
boot.py steps completed
Entered main.py
Listing all files and folders on the boards root directory "/":
['external', 'boot.py', 'lib', 'main.py']
No test file "some-file.txt" exists on external flash "/external", creating it now
Listing all files and folders on the external flash directory "/external":
['some-file.txt']
Finished main.py code. Returning to REPL now
MicroPython v1.18 on 2022-01-17; ESP32 module with ESP32
Type "help()" for more information.
>>>
MPY: soft reboot
manufacturer: 0xef
mem_type: 64
device: 0x4018
capacity: 16777216 bytes
Mounting the external flash to "/external" ...
External flash mounted to "/external"
boot.py steps completed
Entered main.py
Listing all files and folders on the boards root directory "/":
['external', 'boot.py', 'lib', 'main.py']
Test file "some-file.txt" exists on external flash "/external"
This is its content:
Hello World at 698411330

Appending new content to "/external/some-file.txt"
Listing all files and folders on the external flash directory "/external":
['some-file.txt']
Finished main.py code. Returning to REPL now
MicroPython v1.18 on 2022-01-17; ESP32 module with ESP32
Type "help()" for more information.
```

<!-- Links -->
[ref-micropython-winbond-root]: https://github.com/brainelectronics/micropython-winbond/tree/main/
