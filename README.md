# TriloDocs

**A Flask-based tool for extracting and processing tables from .docx files.**

## Features

- Upload a `.docx` file via a web interface.
- Extract and process table data (captions, headers, cell values).
- Download processed results as a JSON file.

## Installation

Follow these steps to set up and run TriloDocs locally:

1. **Clone the repository**  
   ```bash
   git clone https://github.com/denis-liholet/TriloDocs.git
   cd TriloDocs
   ```

2. **Create and activate a virtual environment**  
   ```bash
   python3 -m venv .venv
   # macOS / Linux
   source .venv/bin/activate
   # Windows (PowerShell)
   .venv\\Scripts\\Activate.ps1
   ```

3. **Install application**  
   ```bash
   pip install .
   ```
   In case if you needed editable version:
   ```bash
   pip install -e .
   ```


## Running the Application

Start the Flask development server:

```bash
python run.py
```

By default, the app runs at [http://127.0.0.1:5000/](http://127.0.0.1:5000/).

## Usage

1. Navigate to the upload page.
2. Choose a `.docx` file and click **Process**.
3. After processing, the browser will prompt you to download the JSON result.
4. You’ll be redirected to a thank-you page with an option to process another file.