import json
import hashlib
import shutil
from pathlib import Path
from exceptions.validation import ValidationException
from services.dataStandardisation import standardisation
from services.db import db


class IngestionLayer():
    def __init__(self, base_dir: str = "./sample-data"):
        self.base_dir = Path(base_dir)
        self.raw_dir = self.base_dir / "raw"
        self.duplicates_dir = self.base_dir / "duplicates"
        self.processed_dir = self.base_dir / "processed"
        
        
        # Create if does not exists
        self.raw_dir.mkdir(parents=True,exist_ok=True)
        self.duplicates_dir.mkdir(parents=True,exist_ok=True)
        self.processed_dir.mkdir(parents=True,exist_ok=True)
        
    def generateHash(self,file_content : str) -> str:
        return hashlib.md5(file_content.encode("utf-8")).hexdigest()   # Create a unique hash to avid duplicates
    
    
    def handleDuplicates(self,file_path : Path, reason : str):
        destination_path = self.duplicates_dir / file_path.name
        shutil.move(str(file_path),str(destination_path))
        
        log_file_path = destination_path.with_suffix('.log')
        with open(log_file_path,'w') as logs_file:
            logs_file.write(f"Reason for failure {reason}")
        print(f"File routed to Duplicates - DLQ due to error: {reason}")
    
    def get_total_files(self) -> int:
        file_paths = list(self.raw_dir.glob("*.json"))

        return len(file_paths)
    
    # Logic to handle Input Files
    def process_input_files(self):
        file_paths = list(self.raw_dir.glob("*.json"))
        
        if not file_paths:
            print("No new files found in raw queue.")
            raise ValidationException(404, "No new File found in the input directory")
        
        seen_in_this_batch = set()
        
        # Db Search
        db_init = db.DataBaseEntry()

        for path in file_paths:
            print(f"Reading contents from {path.name}")
            
            try:
                with open(path, 'r', encoding='utf-8') as file:
                    raw_content = file.read()
                
                # Check for file duplicates
                file_hash = self.generateHash(raw_content)
                
                try:
                    payload = json.loads(raw_content)
                except json.JSONDecodeError:
                    raise ValidationException(status_code=422, error_messages="Cannot parse file.")
                
                trace_id = payload.get("traceId")
                datablock = payload.get("data", {})
                response_details = datablock.get("responseDetails", [])
                
                # In-menory search
                if trace_id in seen_in_this_batch:
                    raise ValidationException(400, "Duplicate file caught inside current memory batch.")
                
                if db_init.checkforDuplicates(trace_id):
                    raise ValidationException(400, "Error due to duplication.")
                
                if trace_id:
                    seen_in_this_batch.add(trace_id)
                
                if not response_details:
                    raise ValidationException(status_code=400, error_messages="Missing response details.")
                
                metadata = {}
                for meta_item in payload.get("metaDetails", []):
                    key = meta_item.get("key")
                    if key:
                        metadata[key] = meta_item.get("value")

                has_valid_block = False
                all_records_to_load = []
                
                standardizer = standardisation.StandardizationEngine()
                
                for block in response_details:
                    classifier = block.get("classifier")
                    clinical_data = block.get("data", {})
                    
                    if classifier == "discharge_summary":
                        # Validating the Discharge Rules
                        admission_date = clinical_data.get("admissionDate")
                        if not admission_date:
                            raise ValidationException(status_code=400, error_messages="Discharge summary is missing 'admissionDate'.")
                        has_valid_block = True
                        
                    elif classifier == "lab_report":
                        # Validating the Lab Rules (Look for report details list matching spreadsheet)
                        report_details = clinical_data.get("report_details", [])
                        if not report_details:
                            raise ValidationException(status_code=400, error_messages="Lab report contains empty 'report_details' array.")
                        has_valid_block = True
                
                if not has_valid_block:
                    raise ValidationException(status_code=400, error_messages="File contains have no known medical classifiers.")


                standardized_records = standardizer.standardise_lab_report(payload=payload, metadata_summary=metadata)

                if standardized_records:
                    db_init.add_records(standardized_records)
                    print(f"Successfully loaded {len(standardized_records)} rows into database.")
                else:
                    print("Document processed successfully.")

                print(f"Successfully Ingested data for traceId: {trace_id}")
                
                shutil.move(str(path), str(self.processed_dir / path.name))
                       
            except ValidationException as e:
                self.handleDuplicates(path, reason=str(e.error_messages))
                
            except Exception as e:
                self.handleDuplicates(path, reason=f"Unexpected errors : {str(e)}")
        