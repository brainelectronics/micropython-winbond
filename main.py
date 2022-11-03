#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import time
import os   # os already imported by boot.py. This import is to satisfy flake8

print('Entered main.py')

flash_mount_point = '/external'     # use same as in boot.py
external_test_file_name = 'some-file.txt'
external_test_file_path = flash_mount_point + '/' + external_test_file_name

print('Listing all files and folders on the boards root directory "/":')
# show all files and folders on the boards root directory
# the "external" folder won't be shown anymore
print(os.listdir('/'))
# ['boot.py', 'main.py', 'winbond.py']

if external_test_file_name in os.listdir(flash_mount_point):
    print('Test file "{}" exists on external flash "{}"'.
          format(external_test_file_name, flash_mount_point))

    print('This is its content:')

    # read back the file from the external flash
    with open(external_test_file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            print(line)

    print('Appending new content to "{}"'.format(external_test_file_path))
    # append new content to file on the external flash
    with open(external_test_file_path, 'a') as file:
        file.write('Hello World at {}\n'.format(time.time()))
else:
    print('No test file "{}" exists on external flash "{}", creating it now'.
          format(external_test_file_name, flash_mount_point))

    # append content to file on the external flash, create file is not exists
    with open(external_test_file_path, 'a+') as file:
        file.write('Hello World at {}\n'.format(time.time()))

print('Listing all files and folders on the external flash directory "{}":'.
      format(flash_mount_point))
# show all files and folders on the external flash directory
print(os.listdir(flash_mount_point))
# ['some-file.txt']

print('Finished main.py code. Returning to REPL now')
