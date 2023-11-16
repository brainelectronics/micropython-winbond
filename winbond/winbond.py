#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
Implementation to interact with Winbond W25Q Flash with software reset.

Credits & kudos to crizeo
Taken from https://forum.micropython.org/viewtopic.php?f=16&t=3899
"""

from micropython import const
import time
from machine import SPI, Pin


class W25QFlash(object):
    """W25QFlash implementation"""
    SECTOR_SIZE = const(4096)
    BLOCK_SIZE = const(512)
    PAGE_SIZE = const(256)

    def __init__(self,
                 spi: SPI,
                 cs: Pin,
                 baud: int = 40000000,
                 software_reset: bool = True) -> None:
        """
        Constructs a new instance.

        :param      spi:             The SPI object
        :type       spi:             SPI
        :param      cs:              The CS pin object
        :type       cs:              Pin
        :param      baud:            The SCK clock rate
        :type       baud:            int
        :param      software_reset:  Flag to use software reset
        :type       software_reset:  bool
        """
        self._manufacturer = 0x0
        self._mem_type = 0
        self._device_type = 0x0
        self._capacity = 0

        self.cs = cs
        self.spi = spi
        self.cs.init(self.cs.OUT, value=1)
        # highest possible baudrate is 40 MHz for ESP-12
        self.spi.init(baudrate=baud, phase=1, polarity=1)
        self._busy = False

        if software_reset:
            self.reset()

        # buffer for writing single blocks
        self._cache = bytearray(self.SECTOR_SIZE)

        # calc number of bytes (and makes sure the chip is detected and
        # supported)
        self.identify()

        # address length (default: 3 bytes, 32MB+: 4)
        self._ADR_LEN = 3 if (len(bin(self._capacity - 1)) - 2) <= 24 else 4

        # setup address mode:
        if self._ADR_LEN == 4:
            if not self._read_status_reg(nr=16):  # not in 4-byte mode
                self._await()
                self.cs(0)
                self.spi.write(b'\xB7')  # 'Enter 4-Byte Address Mode'
                self.cs(1)

    @property
    def capacity(self) -> int:
        """
        Get the storage capacity of the flash

        :returns:   Capacity of the flash in bytes
        :rtype:     int
        """
        return self._capacity

    @property
    def device(self) -> int:
        """
        Get the flash device type

        :returns:   Flash device type
        :rtype:     int
        """
        return self._device_type

    @property
    def manufacturer(self) -> int:
        """
        Get the manufacturer ID of the flash

        :returns:   Manufacturer ID of the flash
        :rtype:     int
        """
        return self._manufacturer

    @property
    def mem_type(self) -> int:
        """
        Get the memory type of the flash

        :returns:   Memory type of the flash
        :rtype:     int
        """
        return self._mem_type

    def reset(self) -> None:
        """
        Reset the Winbond flash if the device has no hardware reset pin.

        See datasheet section 7.2.43 Enable Reset (66h) and Reset (99h)
        Because of the small package and the limitation on the number of pins,
        the W25Q64FV provide a software Reset instruction instead of a
        dedicated RESET pin. Once the Reset instruction is accepted, any
        on-going internal operations will be terminated and the device will
        return to its default power-on state and lose all the current volatile
        settings, such as Volatile Status Register bits, Write Enable Latch
        (WEL) status, Program/Erase Suspend status, Read parameter setting
        (P7-P0), Continuous Read Mode bit setting (M7-M0) and Wrap Bit setting
        (W6-W4).
        "Enable Reset (66h)" and "Reset (99h)" instructions can be issued in
        either SPI mode or QPI mode. To avoid accidental reset, both
        instructions must be issued in sequence. Any other commands other than
        "Reset (99h)" after the "Enable Reset (66h)" command will disable the
        "Reset Enable" state. A new sequence of "Enable Reset (66h)" and
        "Reset (99h)" is needed to reset the device. Once the Reset command is
        accepted by the device, the device will take approximately tRST=30us
        to reset. During this period, no command will be accepted.
        Data corruption may happen if there is an on-going or suspended
        internal Erase or Program operation when Reset command sequence is
        accepted by the device. It is recommended to check the BUSY bit and
        the SUS bit in Status Register before issuing the Reset command
        sequence.
        """
        if self._busy:
            self._await()
        self._busy = True
        self.cs(0)
        self.spi.write(b'\x66')  # 'Enable Reset' command
        self.cs(1)
        self.cs(0)
        self.spi.write(b'\x99')  # 'Reset' command
        self.cs(1)
        time.sleep_us(30)
        self._busy = False

    def identify(self) -> None:
        """
        Identify the Winbond chip.

        Determine the manufacturer and device ID and raises an error if the
        device is not detected or not supported.
        The capacity variable is set to the number of blocks (calculated based
        on the detected chip).
        """
        self._await()
        self.cs(0)
        self.spi.write(b'\x9F')  # 'Read JEDEC ID' command

        # manufacturer id, memory type id, capacity id
        mf, mem_type, cap = self.spi.read(3, 0x00)
        self.cs(1)

        self._capacity = int(2**cap)

        if not (mf and mem_type and cap):  # something is 0x00
            raise OSError("device not responding, check wiring. ({}, {}, {})".
                          format(hex(mf), hex(mem_type), hex(cap)))
        if mf != 0xEF or mem_type not in [0x40, 0x60, 0x70]:
            # Winbond manufacturer, Q25 series memory (tested 0x40 only)
            print(f"Warning manufacturer ({hex(mf)}) or memory type"
                  f"({hex(mem_type)}) not tested.")

        self._manufacturer = mf
        self._mem_type = mem_type
        self._device_type = mem_type << 8 | cap

    def get_size(self) -> int:
        """
        Get the flash chip size.

        :returns:   The flash size in byte.
        :rtype:     int
        """
        return self._capacity

    def format(self) -> None:
        """
        Format the Winbond flash chip by resetting all memory to 0xFF.

        Important: Run "os.VfsFat.mkfs(flash)" to make the flash an accessible
        file system. As always, you will then need to run
        "os.mount(flash, '/MyFlashDir')" then to mount the flash
        """
        self._wren()
        self._await()
        self.cs(0)
        self.spi.write(b'\xC7')  # 'Chip Erase' command
        self.cs(1)
        self._await()  # wait for the chip to finish formatting

    def _read_status_reg(self, nr) -> int:
        """
        Read a status register.

        :param      nr:   Register number to read
        :type       nr:   int

        :returns:   The value (0 or 1) in status register (S0, S1, S2, ...)
        :rtype:     int
        """
        reg, bit = divmod(nr, 8)
        self.cs(0)
        # 'Read Status Register-...' (1, 2, 3) command
        self.spi.write((b'\x05', b'\x35', b'\x15')[reg])
        stat = 2**bit & self.spi.read(1, 0xFF)[0]
        self.cs(1)

        return stat

    def _await(self) -> None:
        """
        Wait for device not to be busy
        """
        self._busy = True
        self.cs(0)
        self.spi.write(b'\x05')  # 'Read Status Register-1' command

        # last bit (1) is BUSY bit in stat. reg. byte (0 = not busy, 1 = busy)
        trials = 0
        while 0x1 & self.spi.read(1, 0xFF)[0]:
            if trials > 20:
                raise Exception("Device keeps busy, aborting.")
            time.sleep(0.1)
            trials += 1
        self.cs(1)
        self._busy = False

    def _sector_erase(self, addr) -> None:
        """
        Resets all memory within the specified sector (4kB) to 0xFF

        :param      addr:  The address
        :type       addr:  int
        """
        self._wren()
        self._await()
        self.cs(0)
        self.spi.write(b'\x20')  # 'Sector Erase' command
        self.spi.write(addr.to_bytes(self._ADR_LEN, 'big'))
        self.cs(1)

    def _read(self, buf: list, addr: int) -> None:
        """
        Read the length of the buffer bytes from the chip.

        The buffer length has to be a multiple of self.SECTOR_SIZE (or less).

        :param      buf:   The buffer
        :type       buf:   list
        :param      addr:  The start address
        :type       addr:  int
        """
        assert addr + len(buf) <= self._capacity, \
            "memory not addressable at %s with range %d (max.: %s)" % \
            (hex(addr), len(buf), hex(self._capacity - 1))

        self._await()
        self.cs(0)
        # 'Fast Read' (0x03 = default), 0x0C for 4-byte mode command
        self.spi.write(b'\x0C' if self._ADR_LEN == 4 else b'\x0B')
        self.spi.write(addr.to_bytes(self._ADR_LEN, 'big'))
        self.spi.write(b'\xFF')  # dummy byte
        self.spi.readinto(buf, 0xFF)
        self.cs(1)

    def _wren(self) -> None:
        """
        Set the Write Enable Latch (WEL) bit in the status register
        """
        self._await()
        self.cs(0)
        self.spi.write(b'\x06')  # 'Write Enable' command
        self.cs(1)

    def _write(self, buf: list, addr: int) -> None:
        """
        Write the data of the given buffer to the address location

        Writes the data from <buf> to the device starting at <addr>, which
        has to be erased (0xFF) before. Last byte of <addr> has to be zero,
        which means <addr> has to be a multiple of self.PAGE_SIZE (= start
        of page), because wrapping to the next page (if page size exceeded)
        is implemented for full pages only. Length of <buf> has to be a
        multiple of self.PAGE_SIZE, because only full pages are supported at
        the moment (<addr> will be auto-incremented).

        :param      buf:   The data buffer to write
        :type       buf:   list
        :param      addr:  The starting address
        :type       addr:  int
        """
        assert len(buf) % self.PAGE_SIZE == 0, \
            "invalid buffer length: {}".format(len(buf))
        assert not addr & 0xf, \
            "address ({}) not at page start".format(addr)
        assert addr + len(buf) <= self._capacity, \
            ("memory not addressable at {} with range {} (max.: {})".
                format(hex(addr), len(buf), hex(self._capacity - 1)))

        for i in range(0, len(buf), self.PAGE_SIZE):
            self._wren()
            self._await()
            self.cs(0)
            self.spi.write(b'\x02')  # 'Page Program' command
            self.spi.write(addr.to_bytes(self._ADR_LEN, 'big'))
            self.spi.write(buf[i:i + self.PAGE_SIZE])
            addr += self.PAGE_SIZE
            self.cs(1)

    def _writeblock(self, blocknum: int, buf: list) -> None:
        """
        Write a data block.

        To write a block, the sector (e.g. 4kB = 8 blocks) has to be erased
        first. Therefore, a sector will be read and saved in cache first,
        then the given block will be replaced and the whole sector written
        back when

        :param      blocknum:  The block number
        :type       blocknum:  int
        :param      buf:       The data buffer
        :type       buf:       list
        """
        assert len(buf) == self.BLOCK_SIZE, \
            "invalid block length: {}".format(len(buf))

        sector_nr = blocknum // 8
        sector_addr = sector_nr * self.SECTOR_SIZE
        # index of first byte of page in sector (multiple of self.PAGE_SIZE)
        index = (blocknum << 9) & 0xfff

        self._read(buf=self._cache, addr=sector_addr)
        self._cache[index:index + self.BLOCK_SIZE] = buf  # apply changes
        self._sector_erase(addr=sector_addr)
        # addr is multiple of self.SECTOR_SIZE, so last byte is zero
        self._write(buf=self._cache, addr=sector_addr)

    def readblocks(self, blocknum: int, buf: list) -> None:
        """
        Read a data block. The length has to be a multiple of self.BLOCK_SIZE

        :param      blocknum:  The starting block number
        :type       blocknum:  int
        :param      buf:       The data buffer
        :type       buf:       list
        """
        assert len(buf) % self.BLOCK_SIZE == 0, \
            'invalid buffer length: {}'.format(len(buf))

        buf_len = len(buf)
        if buf_len == self.BLOCK_SIZE:
            self._read(buf=buf, addr=blocknum << 9)
        else:
            offset = 0
            buf_mv = memoryview(buf)
            while offset < buf_len:
                self._read(buf=buf_mv[offset:offset + self.BLOCK_SIZE],
                           addr=blocknum << 9)
                offset += self.BLOCK_SIZE
                blocknum += 1

    def writeblocks(self, blocknum: int, buf: list) -> None:
        """
        Write a data block.The length has to be a multiple of self.BLOCK_SIZE

        :param      blocknum:  The block number
        :type       blocknum:  int
        :param      buf:       The data buffer
        :type       buf:       list
        """
        buf_len = len(buf)
        if buf_len % self.BLOCK_SIZE != 0:
            # appends xFF dummy bytes
            buf += bytearray((self.BLOCK_SIZE - buf_len) * [255])

        if buf_len == self.BLOCK_SIZE:
            self._writeblock(blocknum=blocknum, buf=buf)
        else:
            offset = 0
            buf_mv = memoryview(buf)
            while offset < buf_len:
                self._writeblock(blocknum=blocknum,
                                 buf=buf_mv[offset:offset + self.BLOCK_SIZE])
                offset += self.BLOCK_SIZE
                blocknum += 1
        # remove appended bytes
        buf = buf[:buf_len]

    def count(self) -> int:
        """
        Return the number of blocks available on the device

        :returns:   Number of blocks
        :rtype:     int
        """
        return int(self._capacity / self.BLOCK_SIZE)
