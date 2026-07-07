import re
import json
from datetime import datetime
from typing import Dict, Any, List, Optional


class StandardizationEngine:
    def __init__(self, config_path: str = "./config/schema_dictionary.json"):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        self.name_map = config.get("name_mappings", {})
        self.reference_ranges = config.get("medical_reference_ranges", {})

    def extract_numeric_value(self, raw_result: str) -> tuple[Optional[float], str]:
        if not raw_result:
            return None, ""
        
        clean_str = str(raw_result).strip()
        try:
            match = re.search(r"[-+]?\d*\.\d+|\d+", clean_str)  # Regex for floating point and decimals
            
            if match:
                return float(match.group()), clean_str
        except Exception:
            pass
        return None, clean_str

    # This function is usedto extract low and high values for a range of medical parameters
    def extract_ranges(self, canonical_name: str, raw_range_str: str) -> tuple[Optional[float], Optional[float]]:      
        if raw_range_str and "-" in str(raw_range_str):
            try:
                parts = str(raw_range_str).split("-")
                return float(parts[0].strip()), float(parts[1].strip())
            except ValueError:
                pass
        
        # Fallback to standard baseline dictionary bounds if range parsing string fails
        fallback = self.reference_ranges.get(canonical_name, {})
        return fallback.get("low"), fallback.get("high")

    def determine_analytics(self, test_name: str, val: Optional[float], low: Optional[float], high: Optional[float]) -> str:
        if val is None or not isinstance(val,float):
            return "Invalid/Non-Numeric"

        if test_name == "HAEMOGLOBIN" and (val < 2.0 or val > 30.0):
            return "Outlier"
        if test_name == "WHITE BLOOD CELL COUNT" and (val < 500.0 or val > 100000.0):
            return "Outlier"

        if low is not None and val < low:
            return "Below Range"
        if high is not None and val > high:
            return "Above Range"
            
        return "Within Range"

    def standardise_lab_report(self, payload: dict, metadata_summary: dict) -> List[Dict[str, Any]]:
        output_records = []
        

        trace_id = payload.get("traceId")
        document_id = payload.get("data", {}).get("documentId")
        correlation_id = payload.get("data", {}).get("correlationId")
        
        response_details = payload.get("data", {}).get("responseDetails", [])
        
        for block in response_details:
            if block.get("classifier") != "lab_report":
                continue
                
            inner_data = block.get("data", {})
            basic_info = inner_data.get("basic_info", {})
            report_items = inner_data.get("report_details", [])
            
            for item in report_items:
                raw_test_name = item.get("test_name", "")
                normalized_name = self.name_map.get(raw_test_name.strip().lower(), "UNKNOWN")
                
                num_val, txt_val = self.extract_numeric_value(item.get("result"))
                
                # Standardizing the input unit values
                raw_unit = item.get("unit", "").lower()
                if num_val is not None:
                    if ("mil" in raw_unit or "10^6" in raw_unit) and num_val < 100:
                        num_val = num_val * 1000000
                    
                r_low, r_high = self.extract_ranges(normalized_name, item.get("range"))
                
                test_analytics = self.determine_analytics(normalized_name, num_val, r_low, r_high)
                
                canonical_unit = self.reference_ranges.get(normalized_name, {}).get("unit")
                
                if normalized_name == "HAEMOGLOBIN" and "cell" in raw_unit:
                    test_analytics = "Invalid/Non-Numeric"
                    num_val = None
                

                db_row = {
                    "document_id": document_id,
                    "record_type": "lab_report",
                    "trace_id": trace_id,
                    "correlation_id": correlation_id,
                    "source_system": metadata_summary.get("source_system", "FASTTRACK"),
                    "claim_no": metadata_summary.get("claim_no"),
                    "patient_name": basic_info.get("patient_name"),
                    "age": basic_info.get("age"),
                    "gender": basic_info.get("gender"),
                    "uhid": basic_info.get("uhid"),
                    "reports_date": basic_info.get("reports_date"),
                    
                    "test_name_canonical": normalized_name,
                    "test_name_original": raw_test_name,
                    "result_value": num_val,
                    "result_text": txt_val,
                    "unit_canonical": canonical_unit,
                    "unit_original": item.get("unit"),
                    "range_low": r_low,
                    "range_high": r_high,
                    "range_text": item.get("range"),
                    "test_analytics": test_analytics,
                    "normalization_method": "Config_Lookup_Fuzzy" if normalized_name != "UNKNOWN" else "None",
                    "normalization_confidence": 1.0 if normalized_name != "UNKNOWN" else 0.0,
                    "processed_at": datetime.utcnow().isoformat(),
                    "Test_Name": normalized_name,
                    "Test_Name_Result": num_val if num_val is not None else txt_val,
                    "Test_Name_Range": f"{r_low}-{r_high}" if r_low is not None else item.get("range"),
                    "Test_Name_Unit": canonical_unit,
                    "Test_Name_Analytics": test_analytics
                }
                output_records.append(db_row)
                
        return output_records