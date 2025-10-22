
def preprocess_request_json(data:dict, hospital_meta:dict) -> dict:
    patient_info = {k: v for k, v in data["patient"].items()}

    result = []
    hospital_ids = []
    for hospital in data["candidate_hospitals"]:
        hid = hospital["hospital_id"]
        hospital_ids.append(hid)
        hospital_info = {k: v for k, v in hospital.items() if k != "hospital_id"}
        meta_info = hospital_meta.get(hid, {})
        result.append({
            **patient_info,
            "hospital_id": hid,
            **hospital_info,
            **meta_info
        })

    return result, hospital_ids


def custom_preprocess(data, meta):
    data, ids = preprocess_request_json(data, meta)
    return data, ids


if __name__ == "__main__":
    import json
    from codes.static_resource import load_hospital_meta
    
    with open("test/input_api_schema.json", 'r') as f:
        data = json.load(f)

    print(custom_preprocess(data, load_hospital_meta()))
