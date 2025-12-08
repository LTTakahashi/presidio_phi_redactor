#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for text normalization (encoding artifact cleanup).
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.engine.redaction_engine import RedactionEngine

def test_text_normalization():
    print("="*80)
    print("TEXT NORMALIZATION TEST")
    print("="*80)

    engine = RedactionEngine()
    engine.config['confidence_threshold'] = 0.2
    engine.config['custom_recognizers']['enabled'] = True
    engine._init_analyzer()

    # Test cases from Samina's feedback
    # Using unicode escape sequences to avoid Python parsing issues
    simple_tests = [
        # Smart quotes: â€œ = \xe2\x80\x9c, â€ = \xe2\x80\x9d (when UTF-8 read as Latin-1)
        ('to \u00e2\u20ac\u0153find a place\u00e2\u20ac\u009d at a table', "Smart quotes"),
        # Ellipsis: â€¦ = \xe2\x80\xa6
        ('Water plants \u00e2\u20ac\u00a6 Monday \u00e2\u20ac\u00a6', "Ellipsis"),
        # Apostrophe: â€™ = \xe2\x80\x99
        ("He's getting it together\u00e2\u20ac\u00a6", "Apostrophe and ellipsis"),
        # Leading ellipsis
        ('\u00e2\u20ac\u00a6and future digging at the park', "Leading ellipsis"),
    ]

    all_passed = True
    for input_text, description in simple_tests:
        print(f"\nTesting: {description}")
        print(f"  Input:    '{input_text}'")
        
        # Use analyze_text to get the normalized output
        redacted_text, _ = engine.analyze_text(input_text)
        
        print(f"  Output:   '{redacted_text}'")
        
        # Check if mojibake is removed - look for the characteristic patterns
        mojibake_patterns = ['\u00e2\u20ac\u0153', '\u00e2\u20ac\u009d', '\u00e2\u20ac\u00a6', '\u00e2\u20ac\u2122']
        has_mojibake = any(pattern in redacted_text for pattern in mojibake_patterns)
        
        if has_mojibake:
            print("  \u274c FAILED: Mojibake characters still present")
            all_passed = False
        else:
            print("  \u2713 SUCCESS: Mojibake characters cleaned")

    print("\n" + "="*80)
    if all_passed:
        print("ALL TESTS PASSED!")
    else:
        print("SOME TESTS FAILED")
    print("="*80)

if __name__ == "__main__":
    test_text_normalization()
