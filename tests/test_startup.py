#!/usr/bin/env python3
"""
Startup test for Presidio PHI Redactor.
Tests that the application can be imported and initialized without errors.
"""

import sys
import os

def test_imports():
    """Test that all critical imports work."""
    print("Testing imports...")
    errors = []

    # Add project to path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    # Test core dependencies
    try:
        import presidio_analyzer
        print("  ✓ presidio_analyzer imported")
    except ImportError as e:
        errors.append(f"  ✗ presidio_analyzer: {e}")

    try:
        import presidio_anonymizer
        print("  ✓ presidio_anonymizer imported")
    except ImportError as e:
        errors.append(f"  ✗ presidio_anonymizer: {e}")

    try:
        import spacy
        print("  ✓ spacy imported")
    except ImportError as e:
        errors.append(f"  ✗ spacy: {e}")

    try:
        import openpyxl
        print("  ✓ openpyxl imported")
    except ImportError as e:
        errors.append(f"  ✗ openpyxl: {e}")

    try:
        import pandas
        print("  ✓ pandas imported")
    except ImportError as e:
        errors.append(f"  ✗ pandas: {e}")

    try:
        import yaml
        print("  ✓ yaml imported")
    except ImportError as e:
        errors.append(f"  ✗ yaml: {e}")

    try:
        import tkinter
        print("  ✓ tkinter imported")
    except ImportError as e:
        errors.append(f"  ✗ tkinter: {e}")

    return errors

def test_engine():
    """Test that the redaction engine can be initialized."""
    print("\nTesting RedactionEngine initialization...")
    try:
        from src.engine.redaction_engine import RedactionEngine
        engine = RedactionEngine()
        print("  ✓ RedactionEngine initialized successfully")
        return []
    except Exception as e:
        return [f"  ✗ RedactionEngine initialization failed: {e}"]

def test_gui_import():
    """Test that the GUI can be imported."""
    print("\nTesting GUI import...")
    try:
        from src.gui.app import EnhancedRedactionGUI
        print("  ✓ GUI module imported successfully")
        return []
    except Exception as e:
        return [f"  ✗ GUI import failed: {e}"]

def test_config():
    """Test that configuration can be loaded."""
    print("\nTesting configuration...")
    config_path = os.path.join(os.path.dirname(__file__), "config", "config.yaml")
    if os.path.exists(config_path):
        try:
            import yaml
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            print(f"  ✓ Config loaded successfully from {config_path}")
            return []
        except Exception as e:
            return [f"  ✗ Config loading failed: {e}"]
    else:
        return [f"  ✗ Config file not found at {config_path}"]

def main():
    """Run all startup tests."""
    print("=" * 60)
    print("Presidio PHI Redactor - Startup Test")
    print("=" * 60)

    all_errors = []

    # Run tests
    all_errors.extend(test_imports())
    all_errors.extend(test_config())
    all_errors.extend(test_engine())
    all_errors.extend(test_gui_import())

    # Report results
    print("\n" + "=" * 60)
    if all_errors:
        print("✗ Startup test FAILED with the following errors:")
        for error in all_errors:
            print(error)
        print("\nPlease fix these issues before deployment:")
        print("1. Install missing dependencies: pip install -r requirements.txt")
        print("2. Download spaCy model: python -m spacy download en_core_web_md")
        return 1
    else:
        print("✓ All startup tests PASSED!")
        print("The application is ready to run.")
        print("\nTo start the GUI: python src/gui/app.py")
        print("Or use the launch scripts: ./launch.command (Linux/Mac) or launch.bat (Windows)")
        return 0

if __name__ == "__main__":
    sys.exit(main())