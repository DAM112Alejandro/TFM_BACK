from fastapi import APIRouter , Depends , status , HTTPException
from bson import ObjectId
from db.models.workTypes import WorkTypes 
from db.schemas.workTypesSchema import workTypeListSchema , workTypeSchema  
from db.client import db
from auth.auth import isLogged, isAdmin


router = APIRouter(
    prefix="/workTypes",
    tags=["workTypes"],
    responses={ status.HTTP_404_NOT_FOUND: { "description": "Tipo de trabajo no encontrado" }},
)

@router.get("")
async def get_workType(token = Depends(isAdmin)):
    return workTypeListSchema(db.workTypes.find())

@router.get("/{id}")
async def get_workType_by_id(id , token = Depends(isLogged)):
    found = db.workTypes.find_one({"_id": ObjectId(id)})
    if not found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El tipo de trabajo no existe")
    return workTypeSchema(found)

@router.post("/add", response_model=WorkTypes)
async def add_workType(new_workType: WorkTypes , token = Depends(isAdmin)):
    if db.workType.find_one({ 'description': new_workType.description , "time": new_workType.time  }):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El tipo de trabajo ya existe")
    
    workTypeDict = dict(new_workType)
    id = db.workTypes.insert_one(workTypeDict).inserted_id
    return workTypeSchema(db.workTypes.find_one({"_id": ObjectId(id)}))

@router.put("/update/{id}" , response_model=WorkTypes)
async def update_workType(update_workType: WorkTypes, id, token = Depends(isAdmin)):
    update_data = {
        k: v for k, v in update_workType.model_dump(exclude_unset=True).items()
        if v not in [None ,  ""  , "string" , 0]  
    }
    
    try:
        db.workTypes.update_one({"_id": ObjectId(id)}, {"$set":update_data })
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El tipo de trabajo no existe")
    
    return workTypeSchema(db.workTypes.find_one({"_id": ObjectId(id)}))

@router.delete("/delete/{id}")
async def delete_workType(id, token = Depends(isAdmin)):
    found = db.workTypes.find_one_and_delete({"_id": ObjectId(id)}) 
    if not found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El tipo de trabajo no existe")
  