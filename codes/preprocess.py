
import logging

def _convert_types(data: dict) -> dict:
    converted_data = data.copy()
    
    # Convert all values to string type
    for key, value in converted_data.items():
        if value is not None:
            converted_data[key] = str(value)
        else:
            converted_data[key] = None # Keep None if it's None

    return converted_data

def preprocess_request_json(data:dict, hospital_meta:dict) -> dict:
    patient_info = {k: v for k, v in data["patient"].items()}
    patient_info = _convert_types(patient_info) # Apply type conversion

    TARGET_SCHEMA_KEYS = [
        "age", "sex", "triage_level", "symptom", "bp_systolic", "hr", 
        "icu_beds", "er_beds", "specialist_oncall", "hospital_capacity", 
        "hospital_area", "is_24h", "is_regional_center", "has_er", 
        "distance_km", "eta_minutes"
    ]

    result = []
    hospital_ids = []
    for hospital in data["candidate_hospitals"]:
        hid = hospital["hospital_id"]
        hospital_ids.append(hid)
        hospital_info = {k: v for k, v in hospital.items() if k != "hospital_id"}
        hospital_info = _convert_types(hospital_info) # Apply type conversion
        meta_info = hospital_meta.get(hid, {})
        meta_info = _convert_types(meta_info) # Apply type conversion
        
        combined_info = {
            **patient_info,
            **hospital_info,
            **meta_info
        }
        
        # Filter combined_info to only include keys from TARGET_SCHEMA_KEYS
        filtered_instance = {key: combined_info.get(key) for key in TARGET_SCHEMA_KEYS}
        filtered_instance['triage_level'] = 'Level'+filtered_instance['triage_level']
        result.append(filtered_instance)

    return result, hospital_ids


def custom_preprocess(data, meta):
    data, ids = preprocess_request_json(data, meta)
    return data, ids


if __name__ == "__main__":
    import json
    from codes.static_resource import load_hospital_meta
    
    with open("test/input_api_schema.json", 'r') as f:
        data = json.load(f)

    logging.info(custom_preprocess(data, load_hospital_meta()))
