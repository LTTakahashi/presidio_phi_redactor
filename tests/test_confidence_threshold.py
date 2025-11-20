#!/usr/bin/env python3
"""
Test script to verify confidence threshold functionality
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.engine.redaction_engine import RedactionEngine
from presidio_analyzer import AnalyzerEngine
from src.recognizers.custom_recognizers import get_custom_recognizers

def test_confidence_threshold():
    """Test that confidence threshold is properly applied"""

    # Test text with various entity types
    test_text = "John Smith called at 555-1234. His email is john@example.com and MRN is AB123456"

    print("Testing confidence threshold functionality...")
    print(f"Test text: {test_text}")
    print("-" * 60)

    # Test with different confidence thresholds
    thresholds = [0.1, 0.3, 0.5, 0.7, 0.9]

    for threshold in thresholds:
        print(f"\nTesting with confidence threshold: {threshold}")

        # Create engine with specific threshold
        engine = RedactionEngine()
        engine.config['confidence_threshold'] = threshold

        # Re-initialize with new config
        engine._init_analyzer()

        # Analyze the text
        results = engine.analyzer.analyze(
            text=test_text,
            entities=engine.config.get('enabled_entities', []),
            language='en',
            score_threshold=threshold  # Pass threshold directly
        )

        print(f"  Found {len(results)} entities above threshold {threshold}:")
        for result in results:
            print(f"    - {result.entity_type}: '{test_text[result.start:result.end]}' (score: {result.score:.2f})")

        # Test the _analyze_cell method
        redacted = engine._analyze_cell(test_text, 1, 1, "Sheet1")
        print(f"  Redacted text: {redacted}")

def test_custom_recognizer_scores():
    """Test that custom recognizers adapt to confidence threshold"""

    print("\n" + "="*60)
    print("Testing custom recognizer score adaptation...")
    print("-" * 60)

    thresholds = [0.2, 0.5, 0.8]

    for threshold in thresholds:
        print(f"\nThreshold: {threshold}")

        config = {
            'confidence_threshold': threshold,
            'custom_recognizers': {
                'enabled': True,
                'mrn_pattern': r'\b[A-Z]{2}\d{6}\b'
            }
        }

        recognizers = get_custom_recognizers(config)

        for recognizer in recognizers:
            print(f"  {recognizer.name}:")
            for pattern in recognizer.patterns:
                print(f"    - {pattern.name}: score = {pattern.score:.2f}")

if __name__ == "__main__":
    test_confidence_threshold()
    test_custom_recognizer_scores()
    print("\n✓ Test completed successfully!")