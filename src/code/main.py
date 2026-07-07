from fastapi import FastAPI
from services.ingestion import ingestion
from services.db import db


app = FastAPI(title="Veritas Claims Pipeline", version="0.0.1",terms_of_service="#")
ingestion = ingestion.IngestionLayer()
db_service = db.DataBaseEntry()


@app.get("/",tags=["Health Check and Base Route"])
def root():
    return {
        "success" : True,
        "status_code" : 200,
        "message" : "Backend is running correctly"
    }

@app.get("/health",tags=["Health Check and Base Route"])
def get_health_status():
    return {
        "success" : True,
        "status_code" : 200,
        "message" : "Healthy status for backend"
    }
    
    
@app.post("/api/v1/processing",tags=["Handling Reports"])
def file_processing():
    """
    Ingestion -> Standardization -> Retrieving Records -> Storage
    """
    
    ingestion.process_input_files()
    return {"status": "Execution finished processing the input files"}


@app.get("/retrieve",tags=["DB-Routes"])
def db_retrieve():
    response = db_service.load_db_records()
    
    return {
        "success" : True,
        "status_code" : 200,
        "Records Retrieved" : len(response),
        "response" : response
    }

@app.get("/restart-db",tags=["DB-Routes"])
def restart_db():
    db_service.truncate_db()
    
    return {
        "success" : True,
        "status_code" : 200,
        "message" : "Successfully deleted the values from the DB"
    }
    