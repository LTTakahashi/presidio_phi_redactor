#!/usr/bin/env python3
"""Test script to verify name detection is working"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from presidio_analyzer import AnalyzerEngine

# Test if SpaCy model is available
try:
    import spacy
    nlp = spacy.load("en_core_web_md")
    print("✓ SpaCy model 'en_core_web_md' loaded successfully")
except Exception as e:
    print(f"✗ Failed to load SpaCy model: {e}")
    print("\nTo fix, run: python -m spacy download en_core_web_md")
    sys.exit(1)

# Test Presidio analyzer
analyzer = AnalyzerEngine()

test_cases = [
    "Robert is a patient",
    "Ricardo visited yesterday",
    "The patient John Smith was seen",
    "DOB: 01/01/1980",
    "Email: test@example.com"
]

print("\nTesting name detection with different confidence thresholds:")
print("-" * 60)

for threshold in [0.5, 0.35, 0.20, 0.10, 0.01]:
    print(f"\nConfidence threshold: {threshold}")
    print("-" * 40)

    for text in test_cases:
        results = analyzer.analyze(text=text, entities=["PERSON", "DATE_TIME", "EMAIL_ADDRESS"], language='en')

        detected = []
        for result in results:
            if result.score >= threshold:
                detected.append(f"{text[result.start:result.end]} ({result.entity_type}: {result.score:.2f})")

        if detected:
            print(f"  '{text}' -> {', '.join(detected)}")
        else:
            print(f"  '{text}' -> No detections")

print("\n" + "=" * 60)
print("Raw detection results (all confidence levels):")
print("=" * 60)

for text in test_cases:
    print(f"\n'{text}':")
    results = analyzer.analyze(text=text, entities=["PERSON", "DATE_TIME", "EMAIL_ADDRESS"], language='en')

    if results:
        for result in sorted(results, key=lambda x: x.score, reverse=True):
            print(f"  - {text[result.start:result.end]}: {result.entity_type} (confidence: {result.score:.3f})")
    else:
        print("  - No entities detected")