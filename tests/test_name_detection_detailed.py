#!/usr/bin/env python3
"""
Detailed test for name detection issues
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.engine.redaction_engine import RedactionEngine
from presidio_analyzer import AnalyzerEngine
import spacy

def test_name_detection():
    """Test various name formats and detection issues"""

    print("="*80)
    print("DETAILED NAME DETECTION TEST")
    print("="*80)

    # Test cases with various name formats
    test_cases = [
        # Simple names
        ("John", "Single first name"),
        ("Smith", "Single last name"),
        ("John Smith", "Full name"),
        ("Dr. John Smith", "Name with title"),
        ("John Q. Smith", "Name with middle initial"),

        # Names in context
        ("Patient John arrived", "Name with context word 'Patient'"),
        ("The patient is John Smith", "Full name in sentence"),
        ("Contact Maria for details", "Name after action word"),

        # Common names from custom recognizer
        ("Robert is here", "Common first name (custom)"),
        ("Call Michael please", "Common first name (custom)"),
        ("Maria called yesterday", "Common first name (custom)"),

        # Edge cases
        ("JOHN SMITH", "All caps name"),
        ("john smith", "All lowercase name"),
        ("John-Paul Smith", "Hyphenated first name"),
        ("O'Brien", "Name with apostrophe"),
        ("José García", "Name with accents"),

        # Names that might be missed
        ("Bob", "Nickname"),
        ("Johnny", "Informal name"),
        ("J. Smith", "Initial + last name"),
        ("Smith, John", "Last name first format"),

        # Non-names that might be false positives
        ("The bill is due", "Word 'bill' (not a name)"),
        ("Visit the park", "Word 'park' (not a name)"),
        ("Check the mark", "Word 'mark' (not a name)"),
    ]

    # Test with different confidence thresholds
    thresholds = [0.2, 0.5, 0.7]

    for threshold in thresholds:
        print(f"\n{'='*80}")
        print(f"TESTING WITH CONFIDENCE THRESHOLD: {threshold}")
        print(f"{'='*80}")

        # Create engine with specific threshold
        engine = RedactionEngine()
        engine.config['confidence_threshold'] = threshold
        engine.config['custom_recognizers']['enabled'] = True
        engine._init_analyzer()

        print(f"\n{'Text':<30} {'Description':<25} {'Detected':<10} {'Entities'}")
        print("-"*80)

        for test_text, description in test_cases:
            # Analyze the text
            results = engine.analyzer.analyze(
                text=test_text,
                entities=['PERSON'],  # Only look for persons
                language='en',
                score_threshold=threshold
            )

            detected = "YES" if results else "NO"
            entities_str = ""
            if results:
                entities_info = []
                for r in results:
                    entity_text = test_text[r.start:r.end]
                    entities_info.append(f"{entity_text}({r.score:.2f})")
                entities_str = ", ".join(entities_info)

            print(f"{test_text:<30} {description:<25} {detected:<10} {entities_str}")


def test_spacy_ner_directly():
    """Test SpaCy NER directly to see what it detects"""

    print("\n" + "="*80)
    print("TESTING SPACY NER DIRECTLY")
    print("="*80)

    # Load SpaCy model directly
    try:
        nlp = spacy.load("en_core_web_md")
    except:
        print("ERROR: SpaCy model not loaded. Please run: python -m spacy download en_core_web_md")
        return

    test_texts = [
        "John Smith works at Microsoft",
        "Patient John arrived at 3pm",
        "Robert called yesterday",
        "The patient is Maria Garcia",
        "Contact Dr. Smith immediately",
        "Bob and Alice went to the store",
    ]

    print("\nSpaCy NER Results (without Presidio):")
    print("-"*80)

    for text in test_texts:
        doc = nlp(text)
        print(f"\nText: '{text}'")

        if doc.ents:
            print("Entities found:")
            for ent in doc.ents:
                print(f"  - {ent.text}: {ent.label_} (SpaCy detected)")
        else:
            print("  No entities detected by SpaCy")


def test_analyzer_components():
    """Test what recognizers are actually loaded and working"""

    print("\n" + "="*80)
    print("ANALYZER COMPONENTS TEST")
    print("="*80)

    engine = RedactionEngine()
    engine.config['confidence_threshold'] = 0.2
    engine.config['custom_recognizers']['enabled'] = True
    engine._init_analyzer()

    # Get all recognizers
    recognizers = engine.analyzer.registry.get_recognizers(language='en', entities=['PERSON'])

    print(f"\nRecognizers for PERSON entity:")
    print("-"*40)
    for recognizer in recognizers:
        print(f"  - {recognizer.name}")
        if hasattr(recognizer, 'patterns') and recognizer.patterns:
            print(f"    Patterns: {len(recognizer.patterns)}")

    # Test a specific name with all recognizers
    test_name = "John Smith"
    print(f"\n\nTesting '{test_name}' with each recognizer:")
    print("-"*40)

    for recognizer in recognizers:
        try:
            result = recognizer.analyze(test_name, entities=['PERSON'])
            if result:
                print(f"  {recognizer.name}: DETECTED")
                for r in result:
                    print(f"    - Score: {r.score:.2f}")
            else:
                print(f"  {recognizer.name}: Not detected")
        except Exception as e:
            print(f"  {recognizer.name}: Error - {e}")


def test_specific_problem_names():
    """Test specific names that users report as problematic"""

    print("\n" + "="*80)
    print("TESTING SPECIFIC PROBLEM NAMES")
    print("="*80)

    # Names that users commonly report as not being detected
    problem_names = [
        "John Doe",
        "Jane Smith",
        "Robert Johnson",
        "Maria Garcia",
        "Michael Brown",
        "Sarah Wilson",
        "David Lee",
        "Emily Davis",
        "James Miller",
        "Lisa Anderson",
    ]

    engine = RedactionEngine()
    engine.config['confidence_threshold'] = 0.2  # Very low threshold
    engine.config['custom_recognizers']['enabled'] = True
    engine._init_analyzer()

    print(f"\nTesting common names with threshold 0.2:")
    print("-"*40)

    for name in problem_names:
        # Test the name alone
        results_alone = engine.analyzer.analyze(
            text=name,
            entities=['PERSON'],
            language='en',
            score_threshold=0.2
        )

        # Test the name in a sentence
        sentence = f"The patient is {name}"
        results_sentence = engine.analyzer.analyze(
            text=sentence,
            entities=['PERSON'],
            language='en',
            score_threshold=0.2
        )

        alone_status = "✓" if results_alone else "✗"
        sentence_status = "✓" if any(r for r in results_sentence if name in sentence[r.start:r.end]) else "✗"

        print(f"{name:<20} Alone: {alone_status}  In sentence: {sentence_status}")

        if not results_alone and not results_sentence:
            print(f"  WARNING: '{name}' not detected at all!")


if __name__ == "__main__":
    test_name_detection()
    test_spacy_ner_directly()
    test_analyzer_components()
    test_specific_problem_names()

    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)