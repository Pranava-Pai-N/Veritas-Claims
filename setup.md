# Setup Guide

## Prerequisites
- Python 3.11 or newer
- pip
- A terminal or command prompt

## 1. Clone the repository to your system
```bash
git clone https://github.com/Pranava-Pai-N/Veritas-Claims
```

## 2. Navigate to root src folder
From the repository root, set up the environment variables using commands
```bash
cd src && cp .env.example .env
```

## 3. Navigate to the application folder
From the repository root, move into the source folder:

```bash
cd src/code
```

## 4. Create and activate a virtual environment
On Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

On macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```
### Note : 
- Please install a specific version of python in the virtual environment due to conflicting nature of packages for newer versions of python

    ```bash
    py -3.11 -m venv "your_venv_name"
    ``` 


## 5. Install required dependencies
```bash
pip install -r requirements.txt
```

## 6. Start the backend API
```bash
uvicorn main:app --reload
```

The API will be available at:
- http://127.0.0.1:8000

## 7. Start the Streamlit dashboard
Open a second terminal and run:

```bash
cd src/code/frontend/pages
streamlit run dashboard.py
```

The frontend will be available at:
- http://127.0.0.1:8501

Or use the provided script from the src/code folder:

```bash
./start.sh
```

## 8. Load sample data
The repository already includes sample JSON files in the raw folder. Place additional JSON files in:

```bash
src/code/sample-data/raw
```

Then trigger processing from the dashboard in the sidebar or by calling the processing endpoint.

### Note:
- Please initialise the local db named veritas_claims.db

## 9. Verify the workflow
- Open the dashboard in your browser
- Click the ingestion button or call the processing API
- Review the processed records in the database and dashboard metrics
