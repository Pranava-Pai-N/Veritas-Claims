# Veritas Claims Analytics Pipeline

## Project Overview
Veritas Claims Analytics Pipeline is a lightweight clinical document processing application built to ingest JSON-based medical claim and report files, validate them, standardize lab findings, store them in a local database, and expose the results through both an API and a dashboard.

The project is designed to simulate a simple claims-processing pipeline where incoming medical documents are categorized, cleaned, normalized, and reviewed for outliers or abnormal laboratory values.

## What the Project Does
- Reads JSON files from a raw input folder or GCS Bucket
- Validates required structure and medical content - Ingestion + Standardisation
- Detects duplicate files and routes invalid ones to a separate queue - Log Files/DLQ Folders
- Standardizes lab test names and values using a configurable schema dictionary - Fuzzy Matchup
- Stores processed records in a SQLite database
- Provides a FastAPI backend and a Streamlit dashboard for monitoring and control

## Architecture Summary
The application follows a simple pipeline architecture:

1. Ingestion Layer
   - Reads files from the sample-data/raw directory/GCS Bucket
   - Validates JSON content and business rules
   - Routes duplicates or invalid files to sample-data/duplicates with log files for reasoning
   - Moves successfully processed files to sample-data/processed

2. Standardization Engine
   - Normalizes lab test names using schema mappings
   - Extracts numeric values and reference ranges
   - Classifies values as Within Range, Above Range, Below Range, Outlier, or Invalid/Non-Numeric

3. Database Layer
   - Stores standardized records in SQLite - Further will be extended to a PG DB
   - Prevents duplicate trace IDs from being reloaded
   - Supports retrieval and reset operations

4. Presentation Layer
   - FastAPI exposes backend endpoints for processing and data retrieval
   - Streamlit provides a user-friendly dashboard for monitoring pipeline health

## Codebase Explanation
The implementation is organized under the src/code folder:

- main.py
  - Starts the FastAPI application and exposes the processing and retrieval routes
- services/ingestion/ingestion.py
  - Handles file ingestion, validation, duplicate detection, and file movement across raw/processed/duplicates folders
- services/dataStandardisation/standardisation.py
  - Implements the standardization logic for lab reports and analytics classification
- services/db/db.py
  - Manages SQLite database creation, insertions, duplicate checks, retrieval, and truncation
- frontend/pages/dashboard.py
  - Provides the Streamlit dashboard with charts, metrics, and controls for running ingestion
- config/schema_dictionary.json
  - Stores canonical lab-test mappings and reference ranges used for normalization
- sample-data/
  - Contains sample input JSON files and staging folders for processed and duplicate items

## API Endpoints
The backend exposes the following routes:
- GET / - health check of the backend
- GET /health - service status endpoint
- POST /api/v1/processing - triggers file processing through the ingestion pipeline
- GET /retrieve - returns all stored medical records
- GET /restart-db - clears all database records

## Documentation
Additional project documentation is available in:
- [Project Architecture](docs/architecture.md)
- [Technical Description](docs/technical-description.md)
- [Project Assumptions](docs/assumptions.md)
- [Project Setup](setup.md)


## CodeBase Folder Structure
```bash
Veritas-Claims-Project
├── docs
│   ├── architecture.md
│   ├── assumptions.md
│   └── technical-description.md
├── Readme.md
├── setup.md
└── src
    ├── .env
    ├── .env.example
    ├── .gitignore
    └── code
        ├── config
        │   └── schema_dictionary.json
        ├── exceptions
        │   ├── db.py
        │   ├── validation.py
        │   ├── __init__.py
        ├── frontend
        │   └── pages
        │       └── dashboard.py
        ├── main.py
        ├── requirements.txt
        ├── sample-data
        │   ├── duplicates
        │   ├── processed
        │   └── raw
        │       ├── 5 .json sample files for testing
        ├── services
        │   ├── dataStandardisation
        │   │   ├── standardisation.py
        │   ├── db
        │   │   ├── db.py
        │   └── ingestion
        │       ├── ingestion.py
        │       ├── __init__.py
        ├── start.sh
```

## Setup Instructions
Please follow [setup.md](setup.md) for complete installation and run steps.


## Developed by:
Pranava Pai N

- GitHub: [Pranava-Pai-N](https://github.com/Pranava-Pai-N)
- Website: [Portfolio Website](https://pranava-pai.live/)
- Role: Full-Stack Developer and ML Engineer