# This file is executed on every boot (including wake-boot from deepsleep)
# import esp
# esp.osdebug(None)
# import webrepl
# webrepl.start()

from machine import SPI, Pin
import os
from winbond import W25QFlash, version

os_info = os.uname()
print('MicroPython infos: {}'.format(os_info))
print('Used micropthon-winbond version: {}'.format(version.__version__))

try:
    if 'pyboard' in os_info:
        # NOT YET TESTED !
        # https://docs.micropython.org/en/latest/library/pyb.SPI.html#pyb.SPI
        CS_PIN = Pin(1)
        spi = SPI(1)
    elif 'esp8266' in os_info:
        # NOT YET TESTED !
        # https://docs.micropython.org/en/latest/esp8266/quickref.html#hardware-spi-bus
        # SPI(0) is used for FlashROM and not available to users
        # highest possible baudrate is 40 MHz for ESP-12
        CS_PIN = Pin(1)
        spi = SPI(1)
    elif 'esp32' in os_info:
        # https://docs.micropython.org/en/latest/esp32/quickref.html#hardware-spi-bus
        # Pin   HSPI (id=1)   VSPI (id=2)
        # -------------------------------
        # sck   14            18
        # mosi  13            23
        # miso  12            19
        # cs    x, here 5     x, here 5
        if 'esp32s3' in os_info.machine.lower():
            CS_PIN = Pin(10)
            spi = SPI(2, 2000000, sck=Pin(12), mosi=Pin(11), miso=Pin(13))
        else:
            CS_PIN = Pin(5)
            spi = SPI(2)
    elif 'rp2' in os_info:
        # https://docs.micropython.org/en/latest/rp2/quickref.html#hardware-spi-bus
        # Pin   id=0   id=1
        # -------------------------------
        # sck   6            10
        # mosi  7            11
        # miso  4            8
        # cs    x, here 5    x, here 5
        CS_PIN = Pin(5)
        spi = SPI(0)
    else:
        raise Exception(
            'Unknown device, no default values for CS_PIN and spi defined: {}'.
            format(os_info)
        )
except AttributeError:
    pass
except Exception as e:
    raise e

flash = W25QFlash(spi=spi, cs=CS_PIN, baud=2000000, software_reset=True)

# get Flash infos/properties
print("Flash manufacturer ID: 0x{0:02x}".format(flash.manufacturer))
print("Flash Memory Type: {}".format(flash.mem_type))
print("Flash Device Type: 0x{0:02x}".format(flash.device))
print("Flash size: {} bytes".format(flash.capacity))

flash_mount_point = '/external'

try:
    print('Mounting the external flash to "{}" ...'.format(flash_mount_point))
    os.mount(flash, flash_mount_point)
    print('External flash mounted to "{}"'.format(flash_mount_point))
except Exception as e:
    print('Failed to mount the external flash due to: {}'.format(e))

    if e.errno == 19:
        # [Errno 19] ENODEV aka "No such device"
        # create the filesystem, this takes some seconds (approx. 10 sec)
        print('Creating filesystem for external flash ...')
        print('This might take up to 10 seconds')
        os.VfsFat.mkfs(flash)
        print('Filesystem for external flash created')
    else:
        # takes some seconds/minutes (approx. 40 sec for 128MBit/16MB)
        print('Formatting external flash ...')
        print('This might take up to 60 seconds')
        # !!! only required on the very first start (will remove everything)
        flash.format()
        print('External flash formatted')

        # create the filesystem, this takes some seconds (approx. 10 sec)
        print('Creating filesystem for external flash ...')
        print('This might take up to 10 seconds')
        # !!! only required on first setup and after formatting
        os.VfsFat.mkfs(flash)
        print('Filesystem for external flash created')

    # finally mount the external flash
    os.mount(flash, flash_mount_point)
    print('External flash mounted to "{}"'.format(flash_mount_point))

print('boot.py steps completed')
