from fastapi import FastAPI, Path, HTTPException, Query
import json
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Annotated, Literal, Optional

app = FastAPI()


class Patient(BaseModel):
    id: Annotated[int, Field(..., gt=0, description='ID of the patient', examples=[6])]
    name: Annotated[str, Field(..., min_length=1, description='Name of the patient')]
    age: Annotated[int, Field(..., gt=0, lt=120, description='Age of the patient')]
    gender: Annotated[Literal['Male', 'Female', 'Others'], Field(..., description='Gender of the patient')]
    blood_group: Annotated[Literal['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'], Field(..., description='Blood group of the patient')]
    city: Annotated[str, Field(..., description='City where the patient is living')]
    phone: Annotated[str, Field(..., pattern=r'^\d{10}$', description='10 digit phone number')]
    diagnosis: Annotated[str, Field(..., description='Diagnosis of the patient')]
    height: Annotated[float, Field(..., gt=0, description='Height of the patient in feet')]
    is_admitted: Annotated[bool, Field(default=False, description='Is the patient admitted')]


  

class PatientUpdate(BaseModel):
    name: Annotated[Optional[str], Field(default=None, min_length=1)]
    age: Annotated[Optional[int], Field(default=None, gt=0, lt=120)]
    gender: Annotated[Optional[Literal['Male', 'Female', 'Others']], Field(default=None)]
    blood_group: Annotated[Optional[Literal['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']], Field(default=None)]
    city: Annotated[Optional[str], Field(default=None)]
    phone: Annotated[Optional[str], Field(default=None, pattern=r'^\d{10}$')]
    diagnosis: Annotated[Optional[str], Field(default=None)]
    height: Annotated[Optional[float], Field(default=None, gt=0)]
    is_admitted: Annotated[Optional[bool], Field(default=None)]

def load_data():
    with open('patient.json','r') as f:
        data = json.load(f)
        return data

def save_data(data):
    with open('patient.json', 'w') as f:
        json.dump(data, f, indent=4)


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


@app.post("/create")
def create_patient(patient: Patient):
    # load existing data
    data = load_data()

    # check if the patient already exists
    for p in data["patients"]:
        if p["id"] == patient.id:
            raise HTTPException(status_code=400, detail="Patient already exists")

    # add new patient to the list
    data["patients"].append(patient.model_dump())

    # save into the json file
    save_data(data)

    return JSONResponse(
        status_code=201,
        content={"message": "Patient created successfully"}
    )

@app.put("/edit/{patient_id}")
def update_patient(patient_id: int, patient_update: PatientUpdate):
    data = load_data()

    for patient in data["patients"]:
        if patient["id"] == patient_id:
            # sirf wahi fields lo jo user ne bheji hain
            updated_fields = patient_update.model_dump(exclude_unset=True, exclude_none=True)

            # purane dict mein naye values update karo
            patient.update(updated_fields)

            save_data(data)

            return JSONResponse(
                status_code=200,
                content={"message": "Patient updated successfully", "patient": patient}
            )

    raise HTTPException(status_code=404, detail="Patient not found")


@app.delete("/delete/{patient_id}")
def delete_patient(patient_id: int = Path(..., description="ID of the patient to delete", example=1)):
    data = load_data()

    for index, patient in enumerate(data["patients"]):
        if patient["id"] == patient_id:
            data["patients"].pop(index)
            save_data(data)

            return JSONResponse(
                status_code=200,
                content={"message": "Patient deleted successfully"}
            )

    raise HTTPException(status_code=404, detail="Patient not found")