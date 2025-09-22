#!/usr/bin/env python3
"""Test script for multi-file processing functionality."""

import os
import shutil
from pathlib import Path

print("Testing Multi-File Processing")
print("=" * 60)

# Create test directory structure
test_dir = Path("test_multifile")
output_dir = test_dir / "output"

# Clean up if exists
if test_dir.exists():
    shutil.rmtree(test_dir)

test_dir.mkdir()
output_dir.mkdir()

# Copy the test file multiple times
original_file = "synthetic_phi_tasks.xlsx"

if not os.path.exists(original_file):
    print(f"Error: {original_file} not found")
    exit(1)

# Create 3 test files
test_files = []
for i in range(1, 4):
    test_file = test_dir / f"test_file_{i}.xlsx"
    shutil.copy(original_file, test_file)
    test_files.append(str(test_file))
    print(f"Created: {test_file}")

print(f"\nOutput directory: {output_dir}")
print("\nTest files created successfully!")
print("\nTo test multi-file processing:")
print("1. Run the GUI: python gui_app.py")
print("2. Click 'Select Files...' and select all 3 test files")
print("3. Click 'Choose Folder...' and select the output directory")
print("4. Click 'Redact' to process all files")
print("\nExpected results:")
print("- 3 redacted Excel files in the output folder")
print("- 3 CSV report files in the output folder")
print("- Progress bar should show completion for each file")