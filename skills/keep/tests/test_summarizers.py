#!/usr/bin/env python3
"""
Quick test to compare summarizer performance and quality.
"""
import time
from pathlib import Path
import platform

# Check if we're on Apple Silicon
is_apple_silicon = platform.system() == "Darwin" and platform.machine() == "arm64"

# Get path relative to this test file
DATA_DIR = Path(__file__).parent / "data"

# Read test content - use clean prose (Chinese sutra text)
test_file = DATA_DIR / "fortytwo_chapters.txt"
content = test_file.read_text()[:3000]  # First 3000 chars

print(f"Testing with {len(content)} chars from {test_file.name}")
print("=" * 70)

# Test 1: Truncate (current default)
print("\n1. TRUNCATE SUMMARIZER (current default)")
print("-" * 70)
from keep.providers.summarization import TruncationSummarizer
truncate = TruncationSummarizer(max_length=500)

start = time.time()
truncate_summary = truncate.summarize(content)
truncate_time = time.time() - start

print(f"Time: {truncate_time*1000:.1f}ms")
print(f"Length: {len(truncate_summary)} chars")
print(f"Summary:\n{truncate_summary}")

# Test 2: First Paragraph (middle ground)
print("\n2. FIRST_PARAGRAPH SUMMARIZER (middle ground)")
print("-" * 70)
from keep.providers.summarization import FirstParagraphSummarizer
first_para = FirstParagraphSummarizer(max_length=500)

start = time.time()
para_summary = first_para.summarize(content)
para_time = time.time() - start

print(f"Time: {para_time*1000:.1f}ms")
print(f"Length: {len(para_summary)} chars")
print(f"Summary:\n{para_summary}")

# Test 3: MLX (if available on Apple Silicon)
if is_apple_silicon:
    print("\n3. MLX SUMMARIZER (proposed default for Apple Silicon)")
    print("-" * 70)
    try:
        from keep.providers.mlx import MLXSummarization

        mlx = MLXSummarization()

        start = time.time()
        mlx_summary = mlx.summarize(content, max_length=500)
        mlx_time = time.time() - start

        print(f"Time: {mlx_time*1000:.1f}ms ({mlx_time/truncate_time:.1f}x slower)")
        print(f"Length: {len(mlx_summary)} chars")
        print(f"Summary:\n{mlx_summary}")

        print("\n" + "=" * 70)
        print("RECOMMENDATION:")
        if mlx_time < 5.0:  # Less than 5 seconds is acceptable
            print(f"✅ MLX is fast enough ({mlx_time:.1f}s) - USE AS DEFAULT")
            print("   Quality is much better and latency is acceptable")
        elif para_time < 0.1:  # First paragraph is instant
            print(f"⚠️  MLX is slow ({mlx_time:.1f}s)")
            print(f"✅ USE FIRST_PARAGRAPH AS DEFAULT ({para_time*1000:.1f}ms)")
            print("   Much better than truncate, instant performance")
        else:
            print(f"⚠️  MLX is slow ({mlx_time:.1f}s) - KEEP TRUNCATE AS DEFAULT")
            print("   Quality is better but latency may be too high")

    except (ImportError, RuntimeError) as e:
        print(f"MLX not available: {e}")
        print("Install with: pip install mlx-lm")
else:
    print("\n3. MLX SUMMARIZER")
    print("-" * 70)
    print("Not on Apple Silicon - MLX only works on M1/M2/M3 Macs")
    print("\nRECOMMENDATION:")
    print(f"✅ USE FIRST_PARAGRAPH AS DEFAULT ({para_time*1000:.1f}ms)")
    print("   Much smarter than truncate, still instant")
