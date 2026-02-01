"""
inkjet — Bluetooth thermal printing for humans and machines.

The physical terminal for agents. Zero ink.
"""

__version__ = "0.1.0"
__author__ = "Aaron Chartier"

from inkjet.printer import Printer
from inkjet.discovery import scan_printers

__all__ = ["Printer", "scan_printers", "__version__"]