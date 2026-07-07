# Technical Description

## Backend Service
The backend is built with FastAPI and is initialized in [main.py](../src/code/main.py). It exposes endpoints for health checks, ingestion triggering, record retrieval, and database reset.

## Ingestion Workflow
The ingestion service performs the following operations:
- Scans the raw folder for JSON files
- Reads and parses each document
- Validates the payload format and required clinical sections
- Prevents duplicate trace IDs from being processed repeatedly
- Sends each valid record through the standardization engine
- Writes processed rows to SQLite and moves the source file to the processed queue

## Standardization Logic
The standardization engine uses a dictionary of canonical medical names and reference ranges stored in [Lookup Dictionary](../src/code/config/schema_dictionary.json). It normalizes input values and classifies tests based on the numeric result and reference boundaries.

## Database Design
The project uses SQLite with a single table named medical_records. Each record includes metadata such as document ID, trace ID, correlation ID, patient information, and standardized lab-test outcome details.

## Frontend Dashboard
The Streamlit dashboard reads from the database and the file directories to display:
- processing status
- file counts for raw, processed, and duplicate folders
- analytics summary for test results
- recent processed records

## Technology Stack
- FastAPI - Light weight python framework for Simple, scalable backend, with background jobs
- Streamlit for Frontend
- Plotly - For graphs
- SQLite - Primary DB for local development and prototyping
- Requests - For backend and frontend connections