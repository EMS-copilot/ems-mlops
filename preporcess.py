import csv

def preprocess_request_json(data):
    patient_info = {k: v for k, v in data["patient"].items() if k != "id"}

    hospital_meta = {}
    with open("hospital_meta.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            hospital_meta[row["hospital_id"]] = {k: v for k, v in row.items() if k != "hospital_id"}

    result = {}
    for hospital in data["candidate_hospitals"]:
        hid = hospital["hospital_id"]
        hospital_info = {k: v for k, v in hospital.items() if k != "hospital_id"}
        meta_info = hospital_meta.get(hid, {})  
        result[hid] = {**hospital_info, **patient_info, **meta_info}

    return result

def custom_preprocess(data):
    preprocessed_data = preprocess_request_json(data)
    return preprocessed_data

if __name__ == "__main__":
    import json
    with open("test/input_api_schema.json", 'r') as f:
        data = json.load(f)

    print(custom_preprocess(data))
