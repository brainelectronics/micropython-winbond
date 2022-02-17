#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Test Winbond W25Q Flash on Micropython boards like BE32-01

This test consists of several steps. Not all of them have to be performed
everytime, see the comments of each command.

The flash object is created on SPI2 with a SPI speed of 2kHz, CS on machine
pin 5 and a software reset interface. Check the datasheet of your flash chip.

As a next step a full erase of the complete flash is performed, this is only
required once. If this function is called after something has been stored on
the flash, its content will be permanently lost.
A filesystem will be established with the flash. This step is also only
required once (after a formatting process).

The last step before the flash can be used productively is to mount it at the
desired location. In this case a directory named '/external' is used.
"""

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

# !!! only required on the very first start (will remove everything)
# takes some seconds/minutes!
flash.format()

# !!! only required on first setup and after formatting
# takes some seconds
os.VfsFat.mkfs(flash)

# mount the external flash to /external
os.mount(flash, '/external')

# show all files and folders on the boards root directory
print(os.listdir('/'))
# ['external', 'boot.py', 'main.py', 'winbond.py']

# save a file named 'some-file.txt' to the external flash or extend it
with open('/external/some-file.txt', 'a+') as file:
    file.write('Hello World')

# unmount flash
os.umount('/external')

# show all files and folders on the boards root directory
# the "external" folder won't be shown anymore
print(os.listdir('/'))
# ['boot.py', 'main.py', 'winbond.py']

# mount the external flash again
os.mount(flash, '/external')

# show all files and folders on the external flash
os.listdir('/external')
# ['some-file.txt']

# read back the file from the external flash
with open('/external/some-file.txt', 'r') as file:
    print(file.readlines())
