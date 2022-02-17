# This file is executed on every boot (including wake-boot from deepsleep)
# import esp
# esp.osdebug(None)
# import webrepl
# webrepl.start()

import machine
import os
import winbond

# Pin   HSPI (id=1)   VSPI (id=2)
# -------------------------------
# sck   14            18
# mosi  13            23
# miso  12            19
# cs    x, here 5     x, here 5
flash = winbond.W25QFlash(spi=machine.SPI(2),
                          cs=machine.Pin(5),
                          baud=2000000,
                          software_reset=True)

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
