from fastapi import APIRouter , Depends , status , HTTPException
from bson import ObjectId
from db.models.jobs import Jobs
from db.schemas.jobsSchema import jobSchema, jobListSchema
from db.client import db
from auth.auth import isAdmin, isLogged

router = APIRouter(
    prefix="/trabajos",
    tags=["trabajos"],
    responses={ status.HTTP_404_NOT_FOUND: { "description": "Trabajo no encontrado" }},
)

@router.get("")
async def get_jobs(token = Depends(isAdmin)):
    return jobListSchema(db.jobs.find())

@router.get("/{id}")
async def get_job_by_id(id, token = Depends(isLogged)):
    found = db.jobs.find_one({"_id": ObjectId(id)})
    if not found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El trabajo no existe")
    return jobSchema(found)

@router.get("/user/{id_user}")
async def get_jobs_by_user(id_user, token = Depends(isLogged)):
    found = db.jobs.find({ 'user_id': id_user })
    if not found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trabajos no encontrados")
    return jobListSchema(found)

@router.post("/add", response_model=Jobs)
async def add_job(new_job: Jobs, token = Depends(isAdmin)):
    if db.jobs.find_one({ 'appointment_date': new_job.appointment_date, 'license_plate': new_job.license_plate }):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Trabajo con la misma fecha de cita y matrícula ya existe")
    
    jobDict = dict(new_job)
    id = db.jobs.insert_one(jobDict).inserted_id
    return jobSchema(db.jobs.find_one({"_id": ObjectId(id)}))

@router.put("/update/{id}" , response_model=Jobs)
async def update_job(update_job: Jobs, id ,token = Depends(isLogged)):
    update_data = {
        k: v for k, v in update_job.model_dump(exclude_unset=True).items()
        if v not in [None ,  ""  , "string" , 0]  
    }
    
    try:
        db.jobs.find_one_and_update({"_id": ObjectId(id)}, {"$set":update_data })
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El trabajo no existe")
    
    return jobSchema(db.jobs.find_one({"_id": ObjectId(id)}))

@router.delete("/delete/{id}")
async def delete_job(id, token = Depends(isAdmin)):
    found = db.jobs.find_one_and_delete({"_id": ObjectId(id)}) 
    if not found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El trabajo no existe")
    
@router.put("/status/iniciado/{id}")
async def setStatusIniciado(id, token = Depends(isLogged)):
    found = db.jobs.find_one({"_id": ObjectId(id)})
    if not found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El trabajo no existe")
    status = db.status.find_one({"description": "Iniciado"})
    if not status:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El estado 'Iniciado' no existe")
    db.jobs.find_one_and_update({"_id": ObjectId(id)}, {"$set": {"status_id": str(status["_id"])}})
    
    return jobSchema(db.jobs.find_one({"_id": ObjectId(id)}))
    

@router.put("/status/finalizado/{id}")
async def setStatusFinalizado(id, token = Depends(isLogged)):
    found = db.jobs.find_one({"_id": ObjectId(id)})
    if not found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El trabajo no existe")
    status = db.status.find_one({"description": "Terminado"})
    if not status:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El estado 'Terminado' no existe")
    db.jobs.find_one_and_update({"_id": ObjectId(id)}, {"$set": {"status_id": str(status["_id"])}})
    
    return jobSchema(db.jobs.find_one({"_id": ObjectId(id)}))    