#!/usr/bin/env python3
"""
Test script to reproduce the specific issues reported by the colleague.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.engine.redaction_engine import RedactionEngine

def test_colleague_feedback():
    """
    Test the specific examples provided in the feedback.
    
    Issues reported:
    1. "name":"<PERSON> <PERSON>" (Double redaction?)
    2. "name":"Dr. <PERSON>" (Partial redaction?)
    3. "address":"820 <PERSON>, <LOCATION> 99204" (False positive on address part?)
    4. "name":"DR. KUEHN" (Missed redaction!)
    """
    
    print("="*80)
    print("COLLEAGUE FEEDBACK REPRODUCTION TEST")
    print("="*80)

    # Initialize engine
    engine = RedactionEngine()
    # Use the settings that were likely active (or default)
    engine.config['confidence_threshold'] = 0.2 # Assuming low threshold based on previous context
    engine.config['custom_recognizers']['enabled'] = True
    engine._init_analyzer()

    test_cases = [
        # Case 1: The unredacted doctor name
        {
            "text": "DR. KUEHN",
            "description": "Missed redaction: DR. KUEHN",
            "expected_entities": ["PERSON"]
        },
        # Case 2: The address false positive
        # "820 <PERSON>, <LOCATION> 99204" -> Likely "820 McClellan, Spokane 99204" or similar
        # "Kuehn" is a name, maybe "McClellan" was detected as a name?
        {
            "text": "820 McClellan, Spokane 99204", 
            "description": "Address false positive (McClellan detected as PERSON?)",
            "expected_entities": ["LOCATION"] # Should ideally NOT be PERSON
        },
        # Case 3: Dr. Name format
        {
            "text": "Dr. John Smith",
            "description": "Dr. Name format",
            "expected_entities": ["PERSON"]
        },
        # Case 4: The full JSON-like string context (if possible)
        {
            "text": '{"specialty":"ORTHOPEDIC SHOULDER SURGEON","details":"SURGERY5V12V23","address":"820 McClellan, Spokane 99204","name":"DR. KUEHN","phone":"555-123-4567"}',
            "description": "Full JSON context",
            "expected_entities": ["PERSON", "PHONE_NUMBER", "LOCATION"]
        }
    ]

    for case in test_cases:
        print(f"\nTesting: '{case['text']}' ({case['description']})")
        print("-" * 40)
        
        # Use the new analyze_text method which includes filtering
        redacted_text, results = engine.analyze_text(case['text'])
        
        if not results:
            print("  No entities detected.")
        else:
            for r in results:
                entity_text = case['text'][r.start:r.end]
                print(f"  - {r.entity_type}: '{entity_text}' (Score: {r.score:.2f})")
                
        print(f"  Redacted: {redacted_text}")

if __name__ == "__main__":
    test_colleague_feedback()
