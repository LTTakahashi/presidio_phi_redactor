#!/usr/bin/env python3
"""
Test script to reproduce issues reported by Samina.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.engine.redaction_engine import RedactionEngine

def test_samina_feedback():
    """
    Test the specific feedback points:
    1. Missed locations (hair salon, fire dept)
    2. Partial address redaction
    3. Encoding issues (Saminaâ€™s)
    4. Missed dates (14-8/20, 8-9-24)
    5. False positive <DATE_TIME> for "recurring", "daily", variable names
    """
    
    print("="*80)
    print("SAMINA FEEDBACK REPRODUCTION TEST")
    print("="*80)

    engine = RedactionEngine()
    engine.config['confidence_threshold'] = 0.2
    engine.config['custom_recognizers']['enabled'] = True
    engine._init_analyzer()

    test_cases = [
        # 1. Missed Locations
        {
            "text": "Went to Supercuts Hair Salon yesterday.",
            "description": "Specific Location (Hair Salon)",
            "should_redact": ["Supercuts Hair Salon", "Supercuts"]
        },
        {
            "text": "Visit at Spokane Fire Department Station 1.",
            "description": "Specific Location (Fire Dept)",
            "should_redact": ["Spokane Fire Department Station 1", "Spokane Fire Department"]
        },
        
        # 2. Partial Address (Hypothetical case based on description)
        {
            "text": "1234 W. Main St., Spokane, WA 99201",
            "description": "Full Address",
            "should_redact": ["1234 W. Main St., Spokane, WA 99201"]
        },

        # 3. Encoding Issues
        {
            "text": "It was Saminaâ€™s appointment.",
            "description": "Encoding artifact (Saminaâ€™s)",
            "should_redact": ["Samina"]
        },

        # 4. Missed Dates
        {
            "text": "Date was 14-8/20.",
            "description": "Odd date format (14-8/20)",
            "should_redact": ["14-8/20"]
        },
        {
            "text": "Meeting on 8-9-24.",
            "description": "M-D-YY format",
            "should_redact": ["8-9-24"]
        },

        # 5. False Positives (Should NOT redact)
        {
            "text": "The event is recurring daily.",
            "description": "Recurring/Daily false positive",
            "should_NOT_redact": ["daily", "recurring"]
        },
        {
            "text": "recurringSunday",
            "description": "Variable name 'recurringSunday'",
            "should_NOT_redact": ["recurringSunday", "Sunday"]
        },
        {
            "text": "recurringTuesday",
            "description": "Variable name 'recurringTuesday'",
            "should_NOT_redact": ["recurringTuesday", "Tuesday"]
        }
    ]

    for case in test_cases:
        print(f"\nTesting: '{case['text']}' ({case['description']})")
        print("-" * 40)
        
        redacted_text, results = engine.analyze_text(case['text'])
        
        print(f"  Redacted: {redacted_text}")
        
        # Verification logic
        if 'should_redact' in case:
            for item in case['should_redact']:
                if item in redacted_text:
                    print(f"  ❌ FAILED: '{item}' was NOT redacted.")
                else:
                    print(f"  ✓ SUCCESS: '{item}' was redacted.")
                    
        if 'should_NOT_redact' in case:
            for item in case['should_NOT_redact']:
                if f"<{item.upper()}>" in redacted_text or "<DATE_TIME>" in redacted_text:
                     # Check if the specific item was replaced by a tag
                     # Simple check: if the item is gone and we see a tag
                     if item not in redacted_text:
                         print(f"  ❌ FAILED: '{item}' WAS redacted (False Positive).")
                     else:
                         print(f"  ✓ SUCCESS: '{item}' was NOT redacted.")
                else:
                     print(f"  ✓ SUCCESS: '{item}' was NOT redacted.")

if __name__ == "__main__":
    test_samina_feedback()
