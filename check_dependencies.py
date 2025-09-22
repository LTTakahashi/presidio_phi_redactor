#!/usr/bin/env python3
"""
Dependency checker for Presidio PHI Redactor.
Run this to verify all requirements are properly installed.
"""

import sys
import importlib
from typing import List, Tuple

def check_dependency(module_name: str, package_name: str = None) -> Tuple[bool, str]:
    """Check if a module is installed and can be imported."""
    if package_name is None:
        package_name = module_name

    try:
        importlib.import_module(module_name)
        return True, f"✓ {package_name} is installed"
    except ImportError as e:
        return False, f"✗ {package_name} is NOT installed - Error: {str(e)}"

def check_spacy_model(model_name: str) -> Tuple[bool, str]:
    """Check if a spaCy model is installed."""
    try:
        import spacy
        nlp = spacy.load(model_name)
        return True, f"✓ SpaCy model '{model_name}' is installed"
    except Exception as e:
        return False, f"✗ SpaCy model '{model_name}' is NOT installed - Run: python -m spacy download {model_name}"

def main():
    """Check all dependencies."""
    print("=" * 60)
    print("Presidio PHI Redactor - Dependency Check")
    print("=" * 60)
    print()

    # Core dependencies
    dependencies = [
        ("presidio_analyzer", "presidio-analyzer"),
        ("presidio_anonymizer", "presidio-anonymizer"),
        ("spacy", "spacy"),
        ("openpyxl", "openpyxl"),
        ("pandas", "pandas"),
        ("yaml", "pyyaml"),
        ("tkinter", "tkinter (usually comes with Python)")
    ]

    all_good = True

    print("Checking Python packages:")
    print("-" * 30)
    for module, package in dependencies:
        success, message = check_dependency(module, package)
        print(message)
        if not success:
            all_good = False

    print()
    print("Checking SpaCy models:")
    print("-" * 30)
    success, message = check_spacy_model("en_core_web_md")
    print(message)
    if not success:
        all_good = False

    print()
    print("=" * 60)
    if all_good:
        print("✓ All dependencies are installed correctly!")
        print("You can run the application with: python src/gui/app.py")
        return 0
    else:
        print("✗ Some dependencies are missing.")
        print()
        print("To install all dependencies, run:")
        print("  pip install -r requirements.txt")
        print("  python -m spacy download en_core_web_md")
        return 1

if __name__ == "__main__":
    sys.exit(main())