#!/usr/bin/env python3
"""Test batch processing functionality directly."""

import os
from pathlib import Path
from redaction_engine import RedactionEngine

print("Testing Batch Processing with RedactionEngine")
print("=" * 60)

# Test files
test_dir = Path("test_multifile")
output_dir = test_dir / "output"
test_files = list(test_dir.glob("test_file_*.xlsx"))

if not test_files:
    print("Error: No test files found. Run test_multifile.py first.")
    exit(1)

print(f"Found {len(test_files)} test files")
print(f"Output directory: {output_dir}")

# Initialize engine
engine = RedactionEngine()

# Process each file
results = []
for i, test_file in enumerate(test_files, 1):
    print(f"\nProcessing file {i}/{len(test_files)}: {test_file.name}")

    # Create output path
    output_name = f"{test_file.stem}_redacted{test_file.suffix}"
    output_path = output_dir / output_name

    # Redact
    try:
        output_file, report_file = engine.redact_workbook(
            str(test_file),
            str(output_path)
        )
        results.append((output_file, report_file))
        print(f"  ✓ Redacted: {Path(output_file).name}")
        print(f"  ✓ Report: {Path(report_file).name}")
    except Exception as e:
        print(f"  ✗ Error: {e}")

print("\n" + "=" * 60)
print("RESULTS")
print("=" * 60)
print(f"Successfully processed: {len(results)}/{len(test_files)} files")

# Check output directory
output_files = list(output_dir.glob("*.xlsx"))
report_files = list(output_dir.glob("*.csv"))

print(f"\nOutput directory contents:")
print(f"  - {len(output_files)} Excel files")
print(f"  - {len(report_files)} CSV reports")

if len(results) == len(test_files):
    print("\n✅ Batch processing test PASSED!")
else:
    print("\n❌ Batch processing test FAILED")