#!/usr/bin/env python3
"""
Pants size conversion utilities for international sizing standards.

Handles conversions between US, EU, and UK pant sizing systems.
Primary use case: H&M uses EU sizing which needs conversion for US customers.
"""

from typing import Optional, Dict, Tuple


# Conversion mappings
US_TO_EU_WAIST: Dict[int, int] = {
    26: 36,
    27: 38,
    28: 38,
    29: 40,
    30: 40,
    31: 42,
    32: 44,
    33: 46,
    34: 48,
    36: 50,
    38: 52,
    40: 54,
    42: 56,
    44: 58,
}

EU_TO_US_WAIST: Dict[int, int] = {v: k for k, v in US_TO_EU_WAIST.items()}
# Handle duplicate EU sizes (map to middle US size)
EU_TO_US_WAIST.update({
    38: 28,
    40: 30,
})

US_TO_UK_WAIST: Dict[int, int] = {
    # US and UK waist sizes are generally the same for men's pants
    # Include mapping for completeness
    k: k for k in range(26, 46, 2)
}


class SizeConverter:
    """Utility class for converting pants sizes between US, EU, and UK standards."""

    @staticmethod
    def us_to_eu(us_waist: int) -> Optional[int]:
        """
        Convert US waist size to EU size.

        Args:
            us_waist: US waist size in inches (e.g., 32)

        Returns:
            EU waist size (e.g., 44) or None if no conversion available
        """
        return US_TO_EU_WAIST.get(us_waist)

    @staticmethod
    def eu_to_us(eu_waist: int) -> Optional[int]:
        """
        Convert EU waist size to US size.

        Args:
            eu_waist: EU waist size (e.g., 44)

        Returns:
            US waist size in inches (e.g., 32) or None if no conversion available
        """
        return EU_TO_US_WAIST.get(eu_waist)

    @staticmethod
    def us_to_uk(us_waist: int) -> int:
        """
        Convert US waist size to UK size.

        Note: US and UK men's waist sizes are typically the same.

        Args:
            us_waist: US waist size in inches

        Returns:
            UK waist size (same as US for men's pants)
        """
        return us_waist

    @staticmethod
    def parse_size_string(size_str: str) -> Optional[Tuple[int, Optional[int]]]:
        """
        Parse a size string into waist and inseam components.

        Handles formats like:
        - "32x30" -> (32, 30)
        - "32" -> (32, None)
        - "32W 30L" -> (32, 30)
        - "W32 L30" -> (32, 30)

        Args:
            size_str: Size string to parse

        Returns:
            Tuple of (waist, inseam) where inseam may be None
        """
        size_str = size_str.upper().replace(" ", "")

        # Format: 32x30
        if 'X' in size_str:
            parts = size_str.split('X')
            try:
                waist = int(parts[0])
                inseam = int(parts[1]) if len(parts) > 1 else None
                return (waist, inseam)
            except ValueError:
                return None

        # Format: 32W30L or W32L30
        if 'W' in size_str and 'L' in size_str:
            try:
                w_idx = size_str.index('W')
                l_idx = size_str.index('L')

                if w_idx < l_idx:
                    # 32W30L format
                    waist = int(size_str[:w_idx] if w_idx > 0 else size_str[w_idx+1:l_idx])
                    inseam = int(size_str[l_idx+1:])
                else:
                    # W32L30 format
                    waist = int(size_str[w_idx+1:l_idx])
                    inseam = int(size_str[l_idx+1:])

                return (waist, inseam)
            except (ValueError, IndexError):
                return None

        # Format: Just waist (32)
        try:
            waist = int(size_str)
            return (waist, None)
        except ValueError:
            return None

    @staticmethod
    def format_size(waist: int, inseam: Optional[int] = None, style: str = "us") -> str:
        """
        Format waist and inseam into standard size string.

        Args:
            waist: Waist size
            inseam: Inseam length (optional)
            style: Format style - "us" (32x30), "label" (32W 30L), or "waist_only" (32)

        Returns:
            Formatted size string
        """
        if style == "label":
            if inseam:
                return f"{waist}W {inseam}L"
            return f"{waist}W"
        elif style == "waist_only":
            return str(waist)
        else:  # "us" default
            if inseam:
                return f"{waist}x{inseam}"
            return str(waist)

    @staticmethod
    def convert_size_string(size_str: str, target_system: str) -> Optional[str]:
        """
        Convert a complete size string to a different sizing system.

        Args:
            size_str: Input size string (e.g., "32x30")
            target_system: Target system - "eu", "uk", or "us"

        Returns:
            Converted size string or None if conversion fails
        """
        parsed = SizeConverter.parse_size_string(size_str)
        if not parsed:
            return None

        waist, inseam = parsed

        if target_system.lower() == "eu":
            eu_waist = SizeConverter.us_to_eu(waist)
            if eu_waist is None:
                return None
            return SizeConverter.format_size(eu_waist, inseam, style="us")

        elif target_system.lower() == "uk":
            uk_waist = SizeConverter.us_to_uk(waist)
            return SizeConverter.format_size(uk_waist, inseam, style="us")

        elif target_system.lower() == "us":
            # Already in US, just format consistently
            return SizeConverter.format_size(waist, inseam, style="us")

        return None

    @staticmethod
    def get_eu_size_for_filtering(us_waist: int, inseam: Optional[int] = None) -> str:
        """
        Get EU size formatted for use in H&M filtering.

        Args:
            us_waist: US waist size
            inseam: Optional inseam length

        Returns:
            EU size string for filtering (e.g., "44" or "44x30")
        """
        eu_waist = SizeConverter.us_to_eu(us_waist)
        if eu_waist is None:
            raise ValueError(f"Cannot convert US size {us_waist} to EU")

        if inseam:
            return f"{eu_waist}x{inseam}"
        return str(eu_waist)

    @staticmethod
    def convert_hm_size_to_us(hm_size: str) -> Optional[str]:
        """
        Convert H&M size display to US size.

        H&M may show sizes as "44" (EU) which should convert to "32" (US).

        Args:
            hm_size: H&M size string (EU format)

        Returns:
            US size string or None if conversion fails
        """
        parsed = SizeConverter.parse_size_string(hm_size)
        if not parsed:
            return None

        waist, inseam = parsed

        # If waist is in EU range (typically 36-58), convert to US
        if waist >= 36:
            us_waist = SizeConverter.eu_to_us(waist)
            if us_waist:
                return SizeConverter.format_size(us_waist, inseam, style="us")

        # Otherwise assume already US
        return SizeConverter.format_size(waist, inseam, style="us")


def main():
    """CLI interface for size conversion."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Convert pants sizes between US, EU, and UK")
    parser.add_argument('size', help='Size to convert (e.g., 32, 32x30)')
    parser.add_argument(
        '--to',
        choices=['eu', 'us', 'uk'],
        required=True,
        help='Target sizing system'
    )
    parser.add_argument(
        '--from',
        dest='from_system',
        choices=['eu', 'us', 'uk'],
        default='us',
        help='Source sizing system (default: us)'
    )

    args = parser.parse_args()

    # Parse the input size
    parsed = SizeConverter.parse_size_string(args.size)
    if not parsed:
        print(f"Error: Could not parse size '{args.size}'", file=sys.stderr)
        sys.exit(1)

    waist, inseam = parsed

    # Convert waist based on source and target systems
    if args.from_system == 'us' and args.to == 'eu':
        converted_waist = SizeConverter.us_to_eu(waist)
    elif args.from_system == 'eu' and args.to == 'us':
        converted_waist = SizeConverter.eu_to_us(waist)
    elif args.from_system == 'us' and args.to == 'uk':
        converted_waist = SizeConverter.us_to_uk(waist)
    elif args.from_system == args.to:
        converted_waist = waist
    else:
        print(f"Error: Conversion from {args.from_system} to {args.to} not fully supported", file=sys.stderr)
        sys.exit(1)

    if converted_waist is None:
        print(f"Error: No conversion available for waist size {waist}", file=sys.stderr)
        sys.exit(1)

    # Format output
    result = SizeConverter.format_size(converted_waist, inseam, style="us")
    print(result)


if __name__ == '__main__':
    main()
