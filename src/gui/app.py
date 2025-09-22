#!/usr/bin/env python3
"""
Enhanced GUI application for PHI redaction with collapsible configuration options.
Maintains simple one-click default while exposing advanced settings.
"""

import os
import sys
import threading
import traceback

# Check for critical dependencies before proceeding
try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox, scrolledtext
except ImportError as e:
    print(f"ERROR: Tkinter is not installed. {str(e)}")
    print("Tkinter usually comes with Python. You may need to install python3-tk package.")
    sys.exit(1)

try:
    import yaml
except ImportError as e:
    print(f"ERROR: PyYAML is not installed. {str(e)}")
    print("Please run: pip install pyyaml")
    sys.exit(1)

import re
from pathlib import Path

# Fix import path when running as a script
if __package__ is None or __package__ == '':
    # Running as a script, add parent directories to path
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    try:
        from src.engine.redaction_engine import RedactionEngine
    except ImportError as e:
        print(f"ERROR: Failed to import RedactionEngine. {str(e)}")
        print("This might be due to missing dependencies. Please run:")
        print("  pip install -r requirements.txt")
        print("  python -m spacy download en_core_web_md")
        sys.exit(1)
else:
    # Running as a module
    from ..engine.redaction_engine import RedactionEngine


class EnhancedRedactionGUI:
    """Enhanced GUI with configuration options."""

    # Default entity types
    DEFAULT_ENTITIES = [
        'PERSON', 'EMAIL_ADDRESS', 'PHONE_NUMBER',
        'US_SSN', 'DATE_TIME', 'LOCATION', 'MEDICAL_LICENSE',
        'NRP', 'CREDIT_CARD', 'IP_ADDRESS', 'URL'
    ]

    # Default column hints
    DEFAULT_COLUMN_HINTS = [
        'name', 'patient', 'firstname', 'lastname',
        'dob', 'dateofbirth', 'address', 'phone', 'email',
        'ssn', 'mrn', 'medicalrecord', 'patientid'
    ]

    def __init__(self):
        """Initialize the enhanced GUI application."""
        self.root = tk.Tk()
        self.root.title("PHI Redaction Tool")
        self.root.geometry("720x700")
        self.root.resizable(True, True)  # Allow resizing
        self.root.minsize(720, 500)  # Set minimum size

        # Center the window
        self.root.update_idletasks()
        width = 720
        height = 700
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

        # Instance variables
        self.input_files = []  # Changed to list for multiple files
        self.output_folder = None
        self.output_files = []
        self.report_files = []
        self.processing = False
        self.options_expanded = False
        self.current_file_index = 0
        self.total_files = 0

        # Configuration variables
        self.entity_vars = {}
        self.strategy_var = tk.StringVar(value="replace")
        self.confidence_var = tk.DoubleVar(value=0.5)
        self.custom_pattern_enabled = tk.BooleanVar(value=True)
        self.custom_pattern = tk.StringVar(value=r'\b[A-Z]{2}\d{6}\b')

        # Load default config
        self.load_config()

        self.setup_ui()

    def load_config(self):
        """Load configuration from file if exists."""
        # Find config relative to the application root directory
        app_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        config_path = os.path.join(app_root, "config", "config.yaml")
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)

                    # Load strategy
                    self.strategy_var.set(config.get('anonymization_strategy', 'replace'))

                    # Load confidence threshold
                    # Set to 0.20 by default for better name detection
                    self.confidence_var.set(config.get('confidence_threshold', 0.20))

                    # Load custom pattern if exists
                    custom_config = config.get('custom_recognizers', {})
                    if custom_config:
                        self.custom_pattern_enabled.set(custom_config.get('enabled', True))
                        self.custom_pattern.set(custom_config.get('mrn_pattern', r'\b[A-Z]{2}\d{6}\b'))

            except Exception as e:
                print(f"Could not load config: {e}")

    def setup_ui(self):
        """Set up the user interface with collapsible options."""
        # Configure grid weight for resizing
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Create a canvas and scrollbar for scrolling
        self.canvas = tk.Canvas(self.root, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        # Configure canvas scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        # Create window in canvas
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Bind canvas resize to update frame width
        self.canvas.bind("<Configure>", self._configure_canvas)

        # Pack canvas and scrollbar
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        # Bind mousewheel to canvas for scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

        # Main frame with padding (now inside scrollable_frame)
        main_frame = ttk.Frame(self.scrollable_frame, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Title
        title_label = ttk.Label(
            main_frame,
            text="Excel PHI Redaction Tool",
            font=('Arial', 16, 'bold')
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # Instructions
        instructions = (
            "1. Select an Excel file containing PHI\n"
            "2. Click 'Redact' to process the file\n"
            "3. Download the redacted file and report"
        )
        instructions_label = ttk.Label(
            main_frame,
            text=instructions,
            font=('Arial', 10),
            justify=tk.LEFT
        )
        instructions_label.grid(row=1, column=0, columnspan=3, pady=(0, 20), sticky=tk.W)

        # File selection section
        file_frame = ttk.LabelFrame(main_frame, text="File Selection", padding="10")
        file_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))

        # Input files
        ttk.Label(file_frame, text="Input Files:", font=('Arial', 9, 'bold')).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5)
        )

        self.file_label = ttk.Label(file_frame, text="No files selected", width=50)
        self.file_label.grid(row=1, column=0, padx=(0, 10), sticky=tk.W)

        select_button = ttk.Button(
            file_frame,
            text="Select Files...",
            command=self.select_files,
            width=15
        )
        select_button.grid(row=1, column=1, padx=(0, 5))

        clear_button = ttk.Button(
            file_frame,
            text="Clear",
            command=self.clear_files,
            width=8
        )
        clear_button.grid(row=1, column=2)

        # Output folder
        ttk.Label(file_frame, text="Output Folder:", font=('Arial', 9, 'bold')).grid(
            row=2, column=0, sticky=tk.W, pady=(10, 5)
        )

        self.output_label = ttk.Label(
            file_frame,
            text="Same as input files (default)",
            width=50,
            foreground='gray'
        )
        self.output_label.grid(row=3, column=0, padx=(0, 10), sticky=tk.W)

        output_button = ttk.Button(
            file_frame,
            text="Choose Folder...",
            command=self.select_output_folder,
            width=15
        )
        output_button.grid(row=3, column=1, padx=(0, 5))

        default_button = ttk.Button(
            file_frame,
            text="Use Default",
            command=self.reset_output_folder,
            width=8
        )
        default_button.grid(row=3, column=2)

        # More Options button (collapsible)
        self.options_button = ttk.Button(
            main_frame,
            text="▶ More Options",
            command=self.toggle_options,
            width=20
        )
        self.options_button.grid(row=3, column=0, columnspan=3, pady=10, sticky=tk.W)

        # Options frame (initially hidden)
        self.options_frame = ttk.LabelFrame(
            main_frame,
            text="Advanced Configuration",
            padding="10"
        )

        self.setup_options_panel()

        # Redact button
        self.redact_button = ttk.Button(
            main_frame,
            text="Redact",
            command=self.redact_file,
            state=tk.DISABLED,
            width=20
        )
        self.redact_button.grid(row=5, column=0, columnspan=3, pady=20)

        # Progress bar
        self.progress = ttk.Progressbar(
            main_frame,
            mode='indeterminate',
            length=660
        )
        self.progress.grid(row=6, column=0, columnspan=3, pady=(0, 10))

        # Status label
        self.status_label = ttk.Label(
            main_frame,
            text="Ready",
            font=('Arial', 10)
        )
        self.status_label.grid(row=7, column=0, columnspan=3, pady=(0, 20))

        # Results section (hidden initially)
        self.results_frame = ttk.LabelFrame(
            main_frame,
            text="Results",
            padding="10"
        )

        # Download buttons (in results frame)
        self.download_file_button = ttk.Button(
            self.results_frame,
            text="📥 Download Redacted File",
            command=self.open_output_folder,
            width=25
        )
        self.download_file_button.grid(row=0, column=0, padx=5, pady=5)

        self.download_report_button = ttk.Button(
            self.results_frame,
            text="📊 Download Report",
            command=self.open_report,
            width=25
        )
        self.download_report_button.grid(row=0, column=1, padx=5, pady=5)

        # Output info label
        self.output_info_label = ttk.Label(
            self.results_frame,
            text="",
            font=('Arial', 9),
            wraplength=640
        )
        self.output_info_label.grid(row=1, column=0, columnspan=2, pady=(10, 0))

    def setup_options_panel(self):
        """Set up the collapsible options panel."""
        # Create a notebook for organized tabs
        notebook = ttk.Notebook(self.options_frame)
        notebook.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E))

        # Tab 1: Entity Types
        entities_frame = ttk.Frame(notebook)
        notebook.add(entities_frame, text="Entity Types")

        entities_label = ttk.Label(
            entities_frame,
            text="Select entity types to detect:",
            font=('Arial', 10, 'bold')
        )
        entities_label.grid(row=0, column=0, columnspan=3, pady=5, sticky=tk.W)

        # Create checkboxes for entity types in 3 columns
        for i, entity in enumerate(self.DEFAULT_ENTITIES):
            var = tk.BooleanVar(value=True)
            self.entity_vars[entity] = var

            row = (i // 3) + 1
            col = i % 3

            cb = ttk.Checkbutton(
                entities_frame,
                text=entity,
                variable=var
            )
            cb.grid(row=row, column=col, sticky=tk.W, padx=5, pady=2)

        # Tab 2: Strategy & Confidence
        strategy_frame = ttk.Frame(notebook)
        notebook.add(strategy_frame, text="Strategy")

        # Anonymization Strategy
        strategy_label = ttk.Label(
            strategy_frame,
            text="Anonymization Strategy:",
            font=('Arial', 10, 'bold')
        )
        strategy_label.grid(row=0, column=0, pady=10, sticky=tk.W)

        ttk.Radiobutton(
            strategy_frame,
            text="Replace (e.g., <PERSON>)",
            variable=self.strategy_var,
            value="replace"
        ).grid(row=1, column=0, sticky=tk.W, padx=20)

        ttk.Radiobutton(
            strategy_frame,
            text="Hash (e.g., <PERSON_a1b2c3>)",
            variable=self.strategy_var,
            value="hash"
        ).grid(row=2, column=0, sticky=tk.W, padx=20)

        # Confidence Threshold
        threshold_label = ttk.Label(
            strategy_frame,
            text="Confidence Threshold:",
            font=('Arial', 10, 'bold')
        )
        threshold_label.grid(row=3, column=0, pady=(20, 5), sticky=tk.W)

        threshold_frame = ttk.Frame(strategy_frame)
        threshold_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), padx=20)

        self.confidence_slider = ttk.Scale(
            threshold_frame,
            from_=0.1,
            to=1.0,
            orient=tk.HORIZONTAL,
            variable=self.confidence_var,
            length=300
        )
        self.confidence_slider.grid(row=0, column=0)

        self.confidence_label = ttk.Label(
            threshold_frame,
            text=f"{self.confidence_var.get():.2f}"
        )
        self.confidence_label.grid(row=0, column=1, padx=10)

        # Update label when slider moves
        self.confidence_slider.configure(
            command=lambda v: self.confidence_label.configure(
                text=f"{float(v):.2f}"
            )
        )

        ttk.Label(
            strategy_frame,
            text="Lower = more aggressive, Higher = more precise",
            font=('Arial', 9, 'italic')
        ).grid(row=5, column=0, padx=20, sticky=tk.W)

        # Tab 3: Column Hints
        columns_frame = ttk.Frame(notebook)
        notebook.add(columns_frame, text="Column Hints")

        columns_label = ttk.Label(
            columns_frame,
            text="Column headers that indicate PHI (one per line):",
            font=('Arial', 10, 'bold')
        )
        columns_label.grid(row=0, column=0, pady=5, sticky=tk.W)

        self.column_hints_text = scrolledtext.ScrolledText(
            columns_frame,
            width=50,
            height=6,
            wrap=tk.WORD
        )
        self.column_hints_text.grid(row=1, column=0, padx=5, pady=5)

        # Populate with defaults
        self.column_hints_text.insert('1.0', '\n'.join(self.DEFAULT_COLUMN_HINTS))

        # Tab 4: Custom Patterns
        patterns_frame = ttk.Frame(notebook)
        notebook.add(patterns_frame, text="Custom Patterns")

        # MRN Pattern
        mrn_label = ttk.Label(
            patterns_frame,
            text="Medical Record Number (MRN) Pattern:",
            font=('Arial', 10, 'bold')
        )
        mrn_label.grid(row=0, column=0, columnspan=2, pady=5, sticky=tk.W)

        self.pattern_enabled_cb = ttk.Checkbutton(
            patterns_frame,
            text="Enable custom MRN detection",
            variable=self.custom_pattern_enabled
        )
        self.pattern_enabled_cb.grid(row=1, column=0, sticky=tk.W, pady=5)

        pattern_input_frame = ttk.Frame(patterns_frame)
        pattern_input_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(pattern_input_frame, text="Pattern:").grid(row=0, column=0, padx=(20, 5))

        self.pattern_entry = ttk.Entry(
            pattern_input_frame,
            textvariable=self.custom_pattern,
            width=30
        )
        self.pattern_entry.grid(row=0, column=1)

        self.validate_button = ttk.Button(
            pattern_input_frame,
            text="Validate",
            command=self.validate_pattern,
            width=10
        )
        self.validate_button.grid(row=0, column=2, padx=5)

        # Test input
        ttk.Label(pattern_input_frame, text="Test:").grid(row=1, column=0, padx=(20, 5), pady=5)

        self.test_entry = ttk.Entry(pattern_input_frame, width=30)
        self.test_entry.grid(row=1, column=1, pady=5)
        self.test_entry.insert(0, "AB123456")

        self.test_result_label = ttk.Label(
            pattern_input_frame,
            text="",
            font=('Arial', 9)
        )
        self.test_result_label.grid(row=1, column=2, padx=5, pady=5)

        # Help text
        help_text = (
            "Example: \\b[A-Z]{2}\\d{6}\\b matches AB123456\n"
            "Confidence: 0.8 (high confidence for exact pattern matches)"
        )
        ttk.Label(
            patterns_frame,
            text=help_text,
            font=('Arial', 9, 'italic'),
            foreground='gray'
        ).grid(row=3, column=0, columnspan=2, pady=10, sticky=tk.W, padx=20)

    def _configure_canvas(self, event):
        """Update the canvas window to fill the canvas width."""
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)

    def _on_mousewheel(self, event):
        """Handle mousewheel scrolling."""
        # Windows and MacOS
        if event.delta:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        # Linux
        else:
            if event.num == 4:
                self.canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                self.canvas.yview_scroll(1, "units")

    def toggle_options(self):
        """Toggle the visibility of the options panel."""
        if self.options_expanded:
            self.options_frame.grid_forget()
            self.options_button.configure(text="▶ More Options")
            self.options_expanded = False
        else:
            self.options_frame.grid(row=4, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E))
            self.options_button.configure(text="▼ More Options")
            self.options_expanded = True
            # Ensure the canvas updates its scroll region
            self.root.after(100, lambda: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

    def validate_pattern(self):
        """Validate the custom pattern against test input."""
        pattern = self.custom_pattern.get()
        test_text = self.test_entry.get()

        try:
            regex = re.compile(pattern)
            if regex.search(test_text):
                self.test_result_label.configure(
                    text="✓ Match",
                    foreground='green'
                )
            else:
                self.test_result_label.configure(
                    text="✗ No match",
                    foreground='red'
                )
        except re.error as e:
            self.test_result_label.configure(
                text=f"Invalid: {str(e)[:20]}",
                foreground='red'
            )

    def get_runtime_config(self):
        """Get configuration from GUI controls."""
        config = {
            'enabled_entities': [
                entity for entity, var in self.entity_vars.items()
                if var.get()
            ],
            'anonymization_strategy': self.strategy_var.get(),
            'confidence_threshold': self.confidence_var.get(),
            'column_redaction_hints': [
                hint.strip()
                for hint in self.column_hints_text.get('1.0', tk.END).split('\n')
                if hint.strip()
            ],
            'custom_recognizers': {
                'enabled': self.custom_pattern_enabled.get(),
                'mrn_pattern': self.custom_pattern.get()
            },
            'output_suffix': '_redacted',
            'spacy_model': 'en_core_web_md'
        }
        return config

    def select_files(self):
        """Handle multiple file selection."""
        filenames = filedialog.askopenfilenames(
            title="Select Excel Files",
            filetypes=[
                ("Excel files", "*.xlsx *.xls"),
                ("All files", "*.*")
            ]
        )

        if filenames:
            self.input_files = list(filenames)
            self.update_file_display()
            self.redact_button.config(state=tk.NORMAL)
            self.status_label.config(text=f"{len(self.input_files)} file(s) selected. Ready to redact.")

            # Hide results if switching files
            self.results_frame.grid_forget()

    def clear_files(self):
        """Clear selected files."""
        self.input_files = []
        self.file_label.config(text="No files selected")
        self.redact_button.config(state=tk.DISABLED)
        self.status_label.config(text="Ready")
        self.results_frame.grid_forget()

    def update_file_display(self):
        """Update the file label with selected files."""
        if not self.input_files:
            self.file_label.config(text="No files selected")
            return

        if len(self.input_files) == 1:
            basename = os.path.basename(self.input_files[0])
            if len(basename) > 50:
                display_name = basename[:47] + "..."
            else:
                display_name = basename
            self.file_label.config(text=display_name)
        else:
            # Show count and first file
            first_file = os.path.basename(self.input_files[0])
            if len(first_file) > 30:
                first_file = first_file[:27] + "..."
            display_text = f"{len(self.input_files)} files selected ({first_file}, ...)"
            self.file_label.config(text=display_text)

    def select_output_folder(self):
        """Handle output folder selection."""
        folder = filedialog.askdirectory(
            title="Select Output Folder"
        )

        if folder:
            self.output_folder = folder
            # Truncate for display if needed
            if len(folder) > 50:
                display_path = "..." + folder[-47:]
            else:
                display_path = folder
            self.output_label.config(
                text=display_path,
                foreground='black'
            )

    def reset_output_folder(self):
        """Reset output folder to default (same as input)."""
        self.output_folder = None
        self.output_label.config(
            text="Same as input files (default)",
            foreground='gray'
        )

    def redact_file(self):
        """Handle redaction process with runtime configuration."""
        if not self.input_files:
            messagebox.showwarning("No Files", "Please select files first.")
            return

        if self.processing:
            return

        # Validate files exist
        missing_files = [f for f in self.input_files if not os.path.exists(f)]
        if missing_files:
            messagebox.showerror(
                "File Error",
                f"Selected files no longer exist:\n{', '.join(missing_files)}"
            )
            return

        # Check for existing redacted files
        existing_redacted = []
        for input_file in self.input_files:
            if self.output_folder:
                base_name = os.path.basename(input_file)
                name_parts = os.path.splitext(base_name)
                output_name = f"{name_parts[0]}_redacted{name_parts[1]}"
                output_path = os.path.join(self.output_folder, output_name)
            else:
                base_name = os.path.splitext(input_file)[0]
                output_path = f"{base_name}_redacted.xlsx"

            if os.path.exists(output_path):
                existing_redacted.append(os.path.basename(output_path))

        # If existing redacted files found, ask user for confirmation
        if existing_redacted:
            if len(existing_redacted) == 1:
                message = f"The redacted file '{existing_redacted[0]}' already exists.\nDo you want to replace it?"
            else:
                message = f"The following redacted files already exist:\n{', '.join(existing_redacted[:3])}"
                if len(existing_redacted) > 3:
                    message += f" and {len(existing_redacted) - 3} more..."
                message += "\n\nDo you want to replace them?"

            result = messagebox.askyesno(
                "Replace Existing Files",
                message,
                icon='warning'
            )
            if not result:
                return

        # Start processing in background thread
        self.processing = True
        self.redact_button.config(state=tk.DISABLED)
        self.progress['mode'] = 'determinate'
        self.progress['value'] = 0
        self.status_label.config(text="Processing... Please wait.")

        thread = threading.Thread(target=self._perform_redaction)
        thread.daemon = True
        thread.start()

    def _perform_redaction(self):
        """Perform batch redaction on multiple files."""
        try:
            # Get runtime configuration
            runtime_config = self.get_runtime_config()

            # Create engine with runtime config
            engine = RedactionEngine()

            # Override config with GUI settings
            engine.config = runtime_config

            # Re-initialize analyzer with new config
            engine._init_analyzer()

            # Clear previous outputs
            self.output_files = []
            self.report_files = []

            total_files = len(self.input_files)

            for i, input_file in enumerate(self.input_files):
                # Update status for current file
                file_name = os.path.basename(input_file)
                self.root.after(0, lambda fn=file_name, idx=i+1, total=total_files:
                    self.status_label.config(text=f"Processing file {idx}/{total}: {fn}"))

                # Update progress
                progress = (i / total_files) * 100
                self.root.after(0, lambda p=progress: self.progress.configure(value=p))

                # Determine output location
                if self.output_folder:
                    # Use selected output folder
                    base_name = os.path.basename(input_file)
                    name_parts = os.path.splitext(base_name)
                    output_name = f"{name_parts[0]}{engine.config['output_suffix']}{name_parts[1]}"
                    output_path = os.path.join(self.output_folder, output_name)

                    # Ensure output folder exists
                    os.makedirs(self.output_folder, exist_ok=True)

                    # Perform redaction with custom output path
                    output_file, report_file = engine.redact_workbook(input_file, output_path)
                else:
                    # Use default behavior (same directory as input)
                    output_file, report_file = engine.redact_workbook(input_file)

                self.output_files.append(output_file)
                self.report_files.append(report_file)

            # Final progress update
            self.root.after(0, lambda: self.progress.configure(value=100))

            # Update UI in main thread
            self.root.after(0, self._redaction_complete)

        except Exception as e:
            error_msg = f"Redaction failed:\n{str(e)}\n\nDetails:\n{traceback.format_exc()}"
            self.root.after(0, lambda: self._redaction_error(error_msg))

    def _redaction_complete(self):
        """Handle successful redaction completion."""
        self.processing = False
        self.redact_button.config(state=tk.NORMAL)

        # Update status
        files_count = len(self.output_files)
        self.status_label.config(
            text=f"✓ Successfully redacted {files_count} file(s)!"
        )

        # Show results section
        self.results_frame.grid(row=8, column=0, columnspan=3, pady=(10, 0), sticky=(tk.W, tk.E))

        # Update output info based on number of files
        if self.output_files:
            if self.output_folder:
                # Custom output folder was used
                info_text = (
                    f"Output files saved to: {self.output_folder}\n"
                    f"• {len(self.output_files)} redacted file(s)\n"
                    f"• {len(self.report_files)} report file(s)"
                )
            else:
                # Files saved in their original locations
                if len(self.output_files) == 1:
                    output_dir = os.path.dirname(self.output_files[0])
                    output_name = os.path.basename(self.output_files[0])
                    report_name = os.path.basename(self.report_files[0])
                    info_text = (
                        f"Output files saved to: {output_dir}\n"
                        f"• Redacted file: {output_name}\n"
                        f"• Report: {report_name}"
                    )
                else:
                    # Multiple files in different locations
                    info_text = (
                        f"Successfully redacted {len(self.output_files)} files\n"
                        f"• Files saved in their original directories\n"
                        f"• Each with an accompanying report"
                    )
            self.output_info_label.config(text=info_text)

    def _redaction_error(self, error_msg):
        """Handle redaction error."""
        self.processing = False
        self.progress.stop()
        self.redact_button.config(state=tk.NORMAL)
        self.status_label.config(text="✗ Redaction failed")

        messagebox.showerror("Redaction Error", error_msg)

    def open_output_folder(self):
        """Open the folder containing the output files."""
        if self.output_files and self.output_files[0] and os.path.exists(self.output_files[0]):
            if self.output_folder:
                # Open custom output folder
                folder = self.output_folder
            else:
                # Open first file's folder
                folder = os.path.dirname(self.output_files[0])

            if sys.platform == 'win32':
                os.startfile(folder)
            elif sys.platform == 'darwin':
                os.system(f'open "{folder}"')
            else:  # Linux
                os.system(f'xdg-open "{folder}"')

    def open_report(self):
        """Open the report file(s)."""
        if self.report_files:
            # For multiple reports, open the folder containing them
            if len(self.report_files) > 1:
                self.open_output_folder()
            else:
                # For single report, open it directly
                if self.report_files[0] and os.path.exists(self.report_files[0]):
                    if sys.platform == 'win32':
                        os.startfile(self.report_files[0])
                    elif sys.platform == 'darwin':
                        os.system(f'open "{self.report_files[0]}"')
                    else:  # Linux
                        os.system(f'xdg-open "{self.report_files[0]}"')

    def run(self):
        """Start the GUI application."""
        self.root.mainloop()


def main():
    """Main entry point."""
    try:
        app = EnhancedRedactionGUI()
        app.run()
    except Exception as e:
        messagebox.showerror(
            "Application Error",
            f"Failed to start application:\n{str(e)}"
        )
        sys.exit(1)


if __name__ == '__main__':
    main()