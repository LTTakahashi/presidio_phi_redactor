# Presidio PHI Redactor

Automated PHI (Protected Health Information) detection and redaction tool for Excel files using Microsoft Presidio.

## Quick Start

### Windows
1. Double-click `launch.bat`
2. Wait for dependencies to install (first run only, ~2-3 minutes)
3. GUI opens automatically

### Linux/macOS
1. Run `./launch.command` or `bash launch.command`
2. Wait for dependencies to install (first run only, ~2-3 minutes)
3. GUI opens automatically

### Manual Installation
```bash
# Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_md

# Run application
python src/gui/app.py
```

## How to Use

1. **Select Files** - Click "Browse" to select one or more Excel files
2. **Process** - Click "Redact" to start processing
3. **Get Results** - Redacted files are saved with `_redacted` suffix in the same directory

## Screenshots

### Main Interface
![PHI Redaction Tool Main Screen](./.screenshots/2025-09-22%2009_22_11-PHI%20Redaction%20Tool%20(Ubuntu).png)

### Entity Types: Options
![PHI Redaction Tool Processing](./.screenshots/2025-09-22%2009_23_14-PHI%20Redaction%20Tool%20(Ubuntu).png)

### Strategy: Options
![PHI Redaction Tool Results](./.screenshots/2025-09-22%2009_23_34-PHI%20Redaction%20Tool%20(Ubuntu).png)

## What Gets Redacted

### Automatic Detection
- **Personal Info**: Names, addresses, phone numbers, emails
- **Medical IDs**: SSN, MRN, patient IDs, insurance numbers
- **Dates**: DOB, appointment dates
- **Other PHI**: Credit cards, IP addresses, medical license numbers

### Column-Based Redaction
Columns with these headers are fully redacted:
- Name, Patient, FirstName, LastName
- DOB, DateOfBirth, Address, Phone, Email
- SSN, MRN, PatientID, Insurance

## Configuration

Edit `config/config.yaml` to customize:
- **Entity types** - Which PHI types to detect
- **Confidence threshold** - Detection sensitivity (default: 0.35)
- **Custom patterns** - Organization-specific formats (e.g., MRN pattern)

## Output Files

For each input file, you get:
- `[filename]_redacted.xlsx` - Excel file with PHI removed
- `[filename]_redacted_report.csv` - Detection audit log

## System Requirements

- Python 3.8+
- 4GB RAM recommended
- Windows, macOS, or Linux

## Troubleshooting

### Application won't start
```bash
# Check dependencies
python check_dependencies.py

# Run startup test
python test_startup.py
```

### Missing dependencies
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_md
```

### Linux: No GUI appears
```bash
# Install tkinter
sudo apt-get install python3-tk
```

## Important Notes

 **Always verify results** - Review redacted files before sharing
 **Keep originals secure** - Store original PHI files safely
 **Save audit reports** - Keep detection logs for compliance
 **Test first** - Try on sample data before processing real PHI

## Advanced Features

Click "More Options" in the GUI to:
- Select specific entity types to redact
- Adjust confidence thresholds
- Enable/disable custom patterns
- Choose redaction strategy (replace vs hash)

## Files Structure
```
presidio_phi_redactor/
├── launch.bat          # Windows launcher
├── launch.command      # Linux/Mac launcher
├── requirements.txt    # Python dependencies
├── config/
│   └── config.yaml    # Configuration file
├── src/
│   ├── gui/           # GUI application
│   ├── engine/        # Redaction engine
│   └── recognizers/   # Custom PHI patterns
└── tests/             # Test files
```

# Development

    Luiz Takahashi: l.takahashidosreis@wsu.edu
