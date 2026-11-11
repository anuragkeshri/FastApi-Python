from fastapi import FastAPI, Path, HTTPException, Query
import json

app = FastAPI()


def load_data():
    with open('patient.json','r') as f:
        data = json.load(f)
        return data

@app.get("/")
def hello():
    return{'message': 'hello How Are You? '}


@app.get("/info")
def info():
    return{'message':  "I am Learning fast Api "}

@app.get("/view")
def get_data():
    data = load_data()

    return data

@app.get("/patient/{patient_id}")
def getPatientById(patient_id: int = Path(example=1)):
    data = load_data()

    for patient in data["patients"]:
        if patient["id"] == patient_id:
            return patient

    raise HTTPException(
        status_code=404,
        detail="Patient not found"
    )
    

@app.get("/patientSort")
def sort_Patient(
    sort_by: str = Query(..., description="Sort by age or height"),
    order: str = Query("asc", description="Sort in asc or desc order")
):
    valid_fields = ["age", "height"]
    valid_order = ["asc", "desc"]

    if sort_by not in valid_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid selection. Choose from {valid_fields}"
        )

    if order not in valid_order:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid selection. Choose from {valid_order}"
        )

    data = load_data()

    sort_order = True if order == "desc" else False

    sorted_data = sorted(
        data["patients"],
        key=lambda patient: float(patient.get(sort_by, 0)),
        reverse=sort_order
    )

    return sorted_data
