# Healthcare Provider Data Processor

This program processes healthcare provider data from a CSV file into a SQLite database with full-text search capabilities and provides a web interface for searching providers.

## Requirements

- Python 3.x
- Required packages are listed in `requirements.txt`

## Installation

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Data Import

To import data from a CSV file:

```bash
python process_csv.py path/to/your/csv/file.csv
```

Optional arguments:
- `--db-path`: Specify a custom path for the SQLite database (default: healthcare.db)

Example with custom database path:
```bash
python process_csv.py path/to/your/csv/file.csv --db-path custom_database.db
```

### Web Interface

To start the web interface:

```bash
python app.py
```

The web interface will be available at http://localhost:5000

Features:
- Search providers by name, specialty, sub-specialty, or hospital name
- Full-text search capabilities
- Clean and responsive user interface
- Detailed provider information display

## Full-text Search Capabilities

The following fields are indexed for full-text search:
- First Name
- Last Name
- Middle Name
- Specialty
- Sub Specialty
- Service Location (DBA)

The search is powered by SQLite's FTS5 module for fast and efficient text search. 