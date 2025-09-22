#!/usr/bin/env python3
"""Test the improved redaction with enhanced phone detection."""

from redaction_engine import RedactionEngine
import openpyxl

print("Testing Improved Redaction")
print("=" * 60)

# Initialize engine (will use updated config and custom recognizers)
engine = RedactionEngine()

print(f"\nConfiguration:")
print(f"  Confidence threshold: {engine.config['confidence_threshold']}")
print(f"  Custom recognizers enabled: {engine.config['custom_recognizers']['enabled']}")
print(f"  Enabled entities: {', '.join(engine.config['enabled_entities'][:5])}...")

# Process the file
print("\nProcessing synthetic_phi_tasks.xlsx...")
output_file, report_file = engine.redact_workbook('synthetic_phi_tasks.xlsx')

print(f"✓ Output: {output_file}")
print(f"✓ Report: {report_file}")
print(f"✓ Total detections: {len(engine.detection_log)}")

# Check results
print("\n" + "=" * 60)
print("VERIFICATION")
print("=" * 60)

wb = openpyxl.load_workbook(output_file)
ws = wb.active

# Check specific rows for phone number redaction
test_cases = [
    (2, "Call Maria Gonzalez at (602) 555-1212"),
    (4, "Update the EMR to reflect patient John Doe's change of address to 987 Cedar Blvd."),
]

print("\nChecking phone number redaction:")
for row_idx, original_text in test_cases:
    redacted_value = ws.cell(row=row_idx, column=2).value
    print(f"\nRow {row_idx}:")
    print(f"  Original snippet: ...{original_text[:50]}...")
    print(f"  Redacted: {str(redacted_value)[:80]}")

    # Check if phone numbers are gone
    if redacted_value:
        import re
        phone_pattern = r'\(\d{3}\)\s?\d{3}[\-\.\s]?\d{4}|\d{3}[\-\.\s]\d{3}[\-\.\s]\d{4}'
        if re.search(phone_pattern, str(redacted_value)):
            print(f"  ❌ PHONE NUMBER NOT REDACTED!")
        else:
            print(f"  ✓ Phone number successfully redacted")

# Count entity types detected
from collections import Counter
entity_counts = Counter(d['entity_type'] for d in engine.detection_log)

print("\n" + "=" * 60)
print("DETECTION SUMMARY")
print("=" * 60)
for entity_type, count in entity_counts.most_common():
    print(f"  {entity_type}: {count}")

print("\n✅ Redaction complete with enhanced phone detection!")