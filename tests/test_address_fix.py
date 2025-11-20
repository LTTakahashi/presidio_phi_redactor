#!/usr/bin/env python3
"""
Test script for Address Redaction fixes.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.engine.redaction_engine import RedactionEngine

def test_address_fix():
    print("="*80)
    print("ADDRESS REDACTION FIX TEST")
    print("="*80)

    engine = RedactionEngine()
    engine.config['confidence_threshold'] = 0.2
    engine.config['custom_recognizers']['enabled'] = True
    engine._init_analyzer()

    test_cases = [
        {
            "text": "605 Holland Suite 200",
            "description": "Address without street suffix but with Suite",
            "should_redact": ["605 Holland Suite 200"]
        },
        {
            "text": "601 W 5th SUITE 400",
            "description": "Address with directional and number street",
            "should_redact": ["601 W 5th SUITE 400"]
        },
        {
            "text": "820 McClellan",
            "description": "Number + Name (McClellan might be detected as PERSON, but 820 should be part of address)",
            "should_redact": ["820 McClellan", "820"]
        }
    ]

    for case in test_cases:
        print(f"\nTesting: '{case['text']}' ({case['description']})")
        print("-" * 40)
        
        redacted_text, results = engine.analyze_text(case['text'])
        
        print(f"  Redacted: {redacted_text}")
        
        failed = False
        for item in case['should_redact']:
            if item in redacted_text:
                print(f"  ❌ FAILED: '{item}' was NOT redacted.")
                failed = True
        
        if not failed:
            print(f"  ✓ SUCCESS: Redaction successful.")

if __name__ == "__main__":
    test_address_fix()
