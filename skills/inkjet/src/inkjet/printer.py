"""Bluetooth thermal printer communication."""
import asyncio
import time
from dataclasses import dataclass
from typing import Optional

from bleak import BleakClient, BleakScanner
from bleak.exc import BleakError
import PIL.Image

# BLE Characteristic for printer communication.
# Most inexpensive (X6H, GT01, MX06) use the AE01 service and AE01 characteristic.
PRINTER_CHARACTERISTIC = "0000AE01-0000-1000-8000-00805F9B34FB"

# Printer dimensions
PRINTER_WIDTH_BYTES = 48
PRINTER_WIDTH_PX = PRINTER_WIDTH_BYTES * 8  # 384 pixels

# CRC8 table
CRC8_TABLE = [
    0x00, 0x07, 0x0e, 0x09, 0x1c, 0x1b, 0x12, 0x15, 0x38, 0x3f, 0x36, 0x31,
    0x24, 0x23, 0x2a, 0x2d, 0x70, 0x77, 0x7e, 0x79, 0x6c, 0x6b, 0x62, 0x65,
    0x48, 0x4f, 0x46, 0x41, 0x54, 0x53, 0x5a, 0x5d, 0xe0, 0xe7, 0xee, 0xe9,
    0xfc, 0xfb, 0xf2, 0xf5, 0xd8, 0xdf, 0xd6, 0xd1, 0xc4, 0xc3, 0xca, 0xcd,
    0x90, 0x97, 0x9e, 0x99, 0x8c, 0x8b, 0x82, 0x85, 0xa8, 0xaf, 0xa6, 0xa1,
    0xb4, 0xb3, 0xba, 0xbd, 0xc7, 0xc0, 0xc9, 0xce, 0xdb, 0xdc, 0xd5, 0xd2,
    0xff, 0xf8, 0xf1, 0xf6, 0xe3, 0xe4, 0xed, 0xea, 0xb7, 0xb0, 0xb9, 0xbe,
    0xab, 0xac, 0xa5, 0xa2, 0x8f, 0x88, 0x81, 0x86, 0x93, 0x94, 0x9d, 0x9a,
    0x27, 0x20, 0x29, 0x2e, 0x3b, 0x3c, 0x35, 0x32, 0x1f, 0x18, 0x11, 0x16,
    0x03, 0x04, 0x0d, 0x0a, 0x57, 0x50, 0x59, 0x5e, 0x4b, 0x4c, 0x45, 0x42,
    0x6f, 0x68, 0x61, 0x66, 0x73, 0x74, 0x7d, 0x7a, 0x89, 0x8e, 0x87, 0x80,
    0x95, 0x92, 0x9b, 0x9c, 0xb1, 0xb6, 0xbf, 0xb8, 0xad, 0xaa, 0xa3, 0xa4,
    0xf9, 0xfe, 0xf7, 0xf0, 0xe5, 0xe2, 0xeb, 0xec, 0xc1, 0xc6, 0xcf, 0xc8,
    0xdd, 0xda, 0xd3, 0xd4, 0x69, 0x6e, 0x67, 0x60, 0x75, 0x72, 0x7b, 0x7c,
    0x51, 0x56, 0x5f, 0x58, 0x4d, 0x4a, 0x43, 0x44, 0x19, 0x1e, 0x17, 0x10,
    0x05, 0x02, 0x0b, 0x0c, 0x21, 0x26, 0x2f, 0x28, 0x3d, 0x3a, 0x33, 0x34,
    0x4e, 0x49, 0x40, 0x47, 0x52, 0x55, 0x5c, 0x5b, 0x76, 0x71, 0x78, 0x7f,
    0x6a, 0x6d, 0x64, 0x63, 0x3e, 0x39, 0x30, 0x37, 0x22, 0x25, 0x2c, 0x2b,
    0x06, 0x01, 0x08, 0x0f, 0x1a, 0x1d, 0x14, 0x13, 0xae, 0xa9, 0xa0, 0xa7,
    0xb2, 0xb5, 0xbc, 0xbb, 0x96, 0x91, 0x98, 0x9f, 0x8a, 0x8d, 0x84, 0x83,
    0xde, 0xd9, 0xd0, 0xd7, 0xc2, 0xc5, 0xcc, 0xcb, 0xe6, 0xe1, 0xe8, 0xef,
    0xfa, 0xfd, 0xf4, 0xf3
]


# Commands
class Command:
    RETRACT_PAPER = 0xA0
    FEED_PAPER = 0xA1
    DRAW_BITMAP = 0xA2
    SET_QUALITY = 0xA4
    SET_ENERGY = 0xAF
    SET_SPEED = 0xBD
    SET_DRAWING_MODE = 0xBE


def crc8(data: list[int]) -> int:
    """Calculate CRC8 checksum."""
    crc = 0
    for byte in data:
        crc = CRC8_TABLE[(crc ^ byte) & 0xFF]
    return crc & 0xFF


def format_message(command: int, data: list[int]) -> bytearray:
    """Format a printer command message."""
    # Magic: 0x51 0x78, Command, 0x00, Length, 0x00, Data, CRC8, 0xFF
    msg = [0x51, 0x78, command, 0x00, len(data), 0x00] + data + [crc8(data), 0xFF]
    return bytearray(msg)


class Printer:
    """Bluetooth thermal printer interface."""

    def __init__(self, address: str, energy: Optional[int] = None, speed: Optional[int] = None, quality: Optional[int] = None):
        self.address = address
        self.energy = energy if energy is not None else 9500
        self.speed = speed if speed is not None else 10
        self.quality = quality if quality is not None else 3
        self._client: Optional[BleakClient] = None

    async def connect(self):
        """Connect to the printer."""
        device = await BleakScanner.find_device_by_address(self.address, timeout=20.0)
        if not device:
            raise BleakError(f"Printer not found: {self.address}")
        
        self._client = BleakClient(device)
        await self._client.connect()
        
        # Initialize printer
        await self._init_printer()

    async def disconnect(self):
        """Disconnect from the printer."""
        if self._client:
            await self._client.disconnect()
            self._client = None

    async def _write(self, command: int, data: list[int]):
        """Write a command to the printer."""
        if not self._client:
            raise RuntimeError("Not connected")
        msg = format_message(command, data)
        await self._client.write_gatt_char(PRINTER_CHARACTERISTIC, msg)

    async def set_quality(self, quality: int):
        """Set print quality (1-5, default 3)."""
        self.quality = quality
        await self._write(Command.SET_QUALITY, [quality])

    async def set_energy(self, energy: int):
        """Set print energy/density (little-endian)."""
        self.energy = energy
        await self._write(Command.SET_ENERGY, [energy & 0xFF, (energy >> 8) & 0xFF])

    async def set_speed(self, speed: int):
        """Set print speed."""
        self.speed = speed
        await self._write(Command.SET_SPEED, [speed])

    async def _init_printer(self):
        """Initialize printer settings."""
        await self.set_quality(self.quality)
        await self.set_energy(self.energy)
        await self.set_speed(self.speed)
        # Set drawing mode (0 = image)
        await self._write(Command.SET_DRAWING_MODE, [0])

    async def feed(self, steps: int):
        """Feed paper forward."""
        # Send as blank lines for compatibility
        blank = [0x00] * PRINTER_WIDTH_BYTES
        for _ in range(steps):
            await self._write(Command.DRAW_BITMAP, blank)
            await asyncio.sleep(0.005)

    async def print_image(self, image: PIL.Image.Image):
        """Print a PIL Image."""
        # Convert to RGBA
        image = image.convert("RGBA")
        width = min(image.width, PRINTER_WIDTH_PX)

        for y in range(image.height):
            # Build 48 bytes of 1bpp data (LSB first)
            line = [0x00] * PRINTER_WIDTH_BYTES
            
            for x in range(width):
                r, g, b, a = image.getpixel((x, y))
                # Dark pixels with alpha print as black
                if r < 0x80 and g < 0x80 and b < 0x80 and a > 0x80:
                    byte_idx = x // 8
                    bit_idx = x % 8
                    line[byte_idx] |= (1 << bit_idx)

            await self._write(Command.DRAW_BITMAP, line)
            await asyncio.sleep(0.01)