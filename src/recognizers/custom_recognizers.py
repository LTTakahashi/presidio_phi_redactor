#!/usr/bin/env python3
"""
Custom recognizers for site-specific PHI patterns.
This module provides a simple, extensible way to add custom PII detection.
"""

import re
from typing import List, Dict, Any
from presidio_analyzer import Pattern, PatternRecognizer


def get_custom_recognizers(config: Dict[str, Any]) -> List[PatternRecognizer]:
    """
    Create custom recognizers based on configuration.

    Returns a list of PatternRecognizer objects for site-specific patterns.
    """
    recognizers = []

    custom_config = config.get('custom_recognizers', {})
    if not custom_config.get('enabled', False):
        return recognizers

    # Set fixed confidence scores for pattern matches
    # These represent how confident we are when the pattern matches
    # The threshold will determine if these scores are high enough to trigger redaction

    # Medical Record Number (MRN) Recognizer
    # Example pattern: AB123456 (2 letters followed by 6 digits)
    # Adjust this pattern to match your organization's MRN format
    if 'mrn_pattern' in custom_config:
        mrn_pattern = custom_config['mrn_pattern']

        mrn_recognizer = PatternRecognizer(
            supported_entity="MEDICAL_RECORD_NUMBER",
            name="MRN_recognizer",
            patterns=[
                Pattern(
                    name="MRN_pattern",
                    regex=mrn_pattern,
                    score=0.8  # Fixed high confidence for exact pattern match
                )
            ],
            context=[  # Optional: words that increase confidence when nearby
                "mrn", "medical record", "patient id", "record number",
                "mr#", "medical record number", "patient number"
            ]
        )
        recognizers.append(mrn_recognizer)
    # Doctor Name Recognizer
    # Catches "Dr. Name" or "Doctor Name" formats
    # This is important for surnames that might not be in common name lists
    doctor_pattern = Pattern(
        name="doctor_pattern",
        regex=r'(?i)\b(dr\.?|doctor)\s+([a-z]+(?:-[a-z]+)?)\b',
        score=0.9  # Very high confidence for explicit title
    )

    doctor_recognizer = PatternRecognizer(
        supported_entity="PERSON",
        name="doctor_recognizer",
        patterns=[doctor_pattern],
        context=["physician", "surgeon", "md", "do", "provider"]
    )
    recognizers.append(doctor_recognizer)


    # Common Names Recognizer
    # This catches common first names that SpaCy's NER might miss
    common_first_names = [
        "Robert", "Ricardo", "Richard", "Michael", "John", "David", "James", "William",
        "Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan",
        "Joseph", "Thomas", "Christopher", "Daniel", "Matthew", "Anthony", "Donald",
        "Mark", "Paul", "Steven", "Kenneth", "Andrew", "Joshua", "Kevin", "Brian",
        "George", "Edward", "Ronald", "Timothy", "Jason", "Jeffrey", "Ryan", "Jacob",
        "Gary", "Nicholas", "Eric", "Jonathan", "Stephen", "Larry", "Justin", "Scott",
        "Brandon", "Benjamin", "Samuel", "Frank", "Gregory", "Raymond", "Alexander",
        "Carlos", "Jose", "Luis", "Juan", "Miguel", "Pedro", "Antonio", "Francisco",
        "Maria", "Ana", "Carmen", "Rosa", "Isabel", "Elena", "Teresa", "Patricia",
        "Ahmed", "Mohammed", "Ali", "Hassan", "Ibrahim", "Fatima", "Aisha", "Omar"
    ]

    # Create patterns for each name (case-insensitive)
    name_patterns = []
    for name in common_first_names:
        name_patterns.append(
            Pattern(
                name=f"{name.lower()}_pattern",
                regex=rf'(?i)\b{name}\b',  # (?i) makes it case-insensitive
                score=0.65  # Moderate confidence for common name match
            )
        )

    common_names_recognizer = PatternRecognizer(
        supported_entity="PERSON",
        name="common_names_recognizer",
        patterns=name_patterns,
        context=["patient", "name", "client", "person", "individual", "mr", "ms", "mrs", "dr"]
    )
    recognizers.append(common_names_recognizer)

    # Enhanced Phone Number Recognizer
    # Improves detection of various phone formats
    phone_patterns = [
        # (XXX) XXX-XXXX or (XXX)XXX-XXXX
        Pattern(
            name="phone_with_parentheses",
            regex=r'\(\d{3}\)\s?\d{3}[\-\.\s]?\d{4}',
            score=0.75  # High confidence for this standard format
        ),
        # XXX-XXX-XXXX or XXX.XXX.XXXX or XXX XXX XXXX
        Pattern(
            name="phone_with_separators",
            regex=r'\b\d{3}[\-\.\s]\d{3}[\-\.\s]\d{4}\b',
            score=0.75  # High confidence for standard formats
        ),
        # +1-XXX-XXX-XXXX or +1 (XXX) XXX-XXXX
        Pattern(
            name="phone_with_country",
            regex=r'\+1[\-\.\s]?\(?\d{3}\)?[\-\.\s]?\d{3}[\-\.\s]?\d{4}',
            score=0.85  # Very high confidence with country code
        ),
        # XXX-XXXX (local format)
        Pattern(
            name="phone_local",
            regex=r'\b\d{3}[\-\.\s]\d{4}\b',
            score=0.5  # Lower confidence for ambiguous local format
        ),
        # Common phone number indicators followed by number
        Pattern(
            name="phone_with_label",
            regex=r'(?:phone|tel|cell|mobile|fax|contact)[\s:\-]*[\(]?\d{3}[\)]?[\s\-\.]?\d{3}[\s\-\.]?\d{4}',
            score=0.9  # Very high confidence when labeled
        )
    ]

    enhanced_phone_recognizer = PatternRecognizer(
        supported_entity="PHONE_NUMBER",
        name="enhanced_phone_recognizer",
        patterns=phone_patterns,
        context=["phone", "tel", "telephone", "cell", "mobile", "fax", "contact", "call", "text", "sms"]
    )
    recognizers.append(enhanced_phone_recognizer)

    # Example: Custom ID Pattern
    # Uncomment and modify to add more custom patterns
    """
    if 'custom_id_pattern' in custom_config:
        custom_id_pattern = custom_config['custom_id_pattern']

        custom_id_recognizer = PatternRecognizer(
            supported_entity="CUSTOM_ID",
            name="custom_id_recognizer",
            patterns=[
                Pattern(
                    name="custom_id_pattern",
                    regex=custom_id_pattern,
                    score=0.75
                )
            ],
            context=["id", "identifier", "code"]
        )
        recognizers.append(custom_id_recognizer)
    """

    # Example: Account Number Pattern
    # Pattern: ACCT-XXXXXXXX (ACCT- followed by 8 digits)
    r"""
    account_recognizer = PatternRecognizer(
        supported_entity="ACCOUNT_NUMBER",
        name="account_recognizer",
        patterns=[
            Pattern(
                name="account_pattern",
                regex=r'\bACCT-\d{8}\b',
                score=0.85
            )
        ],
        context=["account", "acct", "account number"]
    )
    recognizers.append(account_recognizer)
    """

    # Example: Employee ID Pattern
    # Pattern: E followed by 5-7 digits
    r"""
    employee_recognizer = PatternRecognizer(
        supported_entity="EMPLOYEE_ID",
        name="employee_recognizer",
        patterns=[
            Pattern(
                name="employee_pattern",
                regex=r'\bE\d{5,7}\b',
                score=0.7
            )
        ],
        context=["employee", "emp", "staff", "worker"]
    )
    recognizers.append(employee_recognizer)
    """

    return recognizers


def validate_mrn(mrn_string: str, pattern: str = r'\b[A-Z]{2}\d{6}\b') -> bool:
    r"""
    Validate if a string matches the MRN pattern.

    Args:
        mrn_string: The string to validate
        pattern: The regex pattern to match against

    Returns:
        True if the string matches the pattern, False otherwise
    """
    return bool(re.match(pattern, mrn_string.strip()))


# Example usage and testing
if __name__ == "__main__":
    # Test the MRN pattern
    test_cases = [
        ("AB123456", True),   # Valid MRN
        ("CD789012", True),   # Valid MRN
        ("A1234567", False),  # Only 1 letter
        ("ABC12345", False),  # 3 letters
        ("AB12345", False),   # Only 5 digits
        ("ab123456", False),  # Lowercase letters
        ("12AB3456", False),  # Numbers before letters
    ]

    pattern = r'\b[A-Z]{2}\d{6}\b'
    print("Testing MRN pattern:", pattern)
    print("-" * 40)

    for test_string, expected in test_cases:
        result = validate_mrn(test_string, pattern)
        status = "✓" if result == expected else "✗"
        print(f"{status} '{test_string}': {result} (expected: {expected})")

    # Example of how custom recognizers would be used
    config = {
        'custom_recognizers': {
            'enabled': True,
            'mrn_pattern': r'\b[A-Z]{2}\d{6}\b'
        }
    }

    recognizers = get_custom_recognizers(config)
    print(f"\nCreated {len(recognizers)} custom recognizer(s)")
    for rec in recognizers:
        print(f"  - {rec.name}: detects {rec.supported_entities}")