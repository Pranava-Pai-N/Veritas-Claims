import sqlite3
from typing import List, Dict, Any
from exceptions.db import DBException


class DataBaseEntry:
    def __init__(self, db_path: str = "veritas_claims.db"):
        self.db_path = db_path
        self.initialise_db()
        
    def initialise_db(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS medical_records (
                        id TEXT PRIMARY KEY,
                        document_id TEXT,
                        record_type TEXT,
                        trace_id TEXT,
                        correlation_id TEXT,
                        source_system TEXT,
                        claim_no TEXT,
                        patient_name TEXT,
                        age TEXT,
                        gender TEXT,
                        uhid TEXT,
                        reports_date TEXT,
                        test_name_canonical TEXT,
                        test_name_original TEXT,
                        result_value REAL,
                        result_text TEXT,
                        unit_canonical TEXT,
                        unit_original TEXT,
                        range_low REAL,
                        range_high REAL,
                        range_text TEXT,
                        test_analytics TEXT,
                        normalization_method TEXT,
                        normalization_confidence REAL,
                        processed_at TEXT,
                        Test_Name   TEXT,
                        Test_Name_Result  TEXT,
                        Test_Name_Range   TEXT,
                        Test_Name_Unit   TEXT,
                        Test_Name_Analytics  TEXT
                    );
                """
                )
                
                conn.commit()
        except DBException as e:
            raise DBException(500,f"Error initialising the database. Please try again later,{e}")
            
    def load_db_records(self) ->  List[Dict]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM medical_records")
                
                rows = cursor.fetchall()
                
                return [dict(row) for row in rows]
        except DBException as e:
            raise DBException(500,f"Error retrieving records from the database,{e}")
            
    def add_records(self, records : List[Dict[str,Any]]):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = """
                    INSERT INTO medical_records (
                        id, document_id,record_type, trace_id, correlation_id, source_system, claim_no,
                        patient_name, age, gender, uhid, reports_date, test_name_canonical, test_name_original,
                        result_value, result_text, unit_canonical, unit_original, range_low, range_high,
                        range_text, test_analytics, normalization_method, normalization_confidence, processed_at,Test_Name,Test_Name_Result,Test_Name_Range,Test_Name_Unit,Test_Name_Analytics
                    ) VALUES (
                        :id, :document_id,:record_type, :trace_id, :correlation_id, :source_system, :claim_no,
                        :patient_name, :age, :gender, :uhid, :reports_date, :test_name_canonical, :test_name_original,
                        :result_value, :result_text, :unit_canonical, :unit_original, :range_low, :range_high,
                        :range_text, :test_analytics, :normalization_method, :normalization_confidence, :processed_at, :Test_Name, :Test_Name_Result, :Test_Name_Range, :Test_Name_Unit, :Test_Name_Analytics
                    ) ON CONFLICT(id) DO UPDATE SET processed_at = excluded.processed_at;
                """
                
                for row in records:
                    row["id"] = f"{row['document_id']}_{row['test_name_original'].replace(' ', '_')}"
                    
                    cursor.execute(query,row)
                    
                conn.commit()     
        except DBException as e:
            raise DBException(500,f"Error inserting values to the database, {e}")
        
    
    def truncate_db(self):   # Removes all values but keep structure same
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("DELETE FROM medical_records")
                                
                conn.commit()
                
                conn.execute("VACUUM")   # Used to claim back the db space used
                
        except DBException as e:
            raise DBException(500,f"Error truncating the Database, {e}")
        
    
    def checkforDuplicates(self, trace_id : str) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                if not trace_id:
                    return False
                
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("SELECT 1 FROM medical_records WHERE trace_id=? LIMIT 1",(str(trace_id),))
                
                row = cursor.fetchone()
                if row is not None:  # Not found
                    return True
                
        except sqlite3.Error as e:
            print(f"Error checking for duplicates,{e}")
            return False

    def load_db_records(self) ->  List[Dict]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM medical_records")
                
                rows = cursor.fetchall()
                
                return [dict(row) for row in rows]
        except DBException as e:
            raise DBException(500,f"Error retrieving records from the database,{e}")
                