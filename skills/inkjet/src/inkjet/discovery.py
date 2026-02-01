"""Bluetooth printer discovery."""
from dataclasses import dataclass
from typing import List
from bleak import BleakScanner

PRINTER_NAMES = ["GT01", "MX06", "X6", "GB01", "GB02", "GB03"]


@dataclass
class PrinterInfo:
    """Information about a discovered printer."""
    name: str
    address: str
    rssi: int = None


async def scan_printers(timeout: int = 10) -> List[PrinterInfo]:
    """Scan for Bluetooth thermal printers."""
    try:
        devices = await BleakScanner.discover(timeout=timeout)
    except Exception as e:
        from .output import print_error
        if "turned off" in str(e):
            print_error("Bluetooth is turned off. Please turn it ON in System Settings.")
        elif "authorized" in str(e) or "privacy" in str(e).lower():
            print_error("Bluetooth access denied. Please allow Bluetooth access in macOS Privacy Settings and try again.")
        else:
            print_error(f"Bluetooth scan failed: {e}")
        return []

    printers = []
    
    for device in devices:
        name = device.name or ""
        # Check if device name matches known printer names (case-insensitive)
        if any(pn.upper() in name.upper() for pn in PRINTER_NAMES):
            printers.append(PrinterInfo(
                name=name,
                address=device.address,
                rssi=getattr(device, 'rssi', None)
            ))
    
    return printers