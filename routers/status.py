from fastapi import APIRouter , Depends , status , HTTPException
from bson import ObjectId
from db.models.status import Status 
from db.schemas.statusSchema import statusSchema , statusListSchema  
from db.client import db
from auth.auth import isLogged, isAdmin


router = APIRouter(
    prefix="/status",
    tags=["status"],
    responses={ status.HTTP_404_NOT_FOUND: { "description": "Estado no encontrado" }},
)

@router.get("")
async def get_status(token = Depends(isAdmin)):
    return statusListSchema(db.status.find())

@router.get("/{id}")
async def get_status_by_id(id, token = Depends(isLogged)):
    found = db.status.find_one({"_id": ObjectId(id)})
    if not found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El estado no existe")
    return statusSchema(found)

@router.post("/add", response_model=Status)
async def add_status(new_status: Status, token = Depends(isAdmin)) :
    if db.status.find_one({ 'description': new_status.description }):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El estado ya existe")
    
    statusDict = dict(new_status)
    id = db.status.insert_one(statusDict).inserted_id
    return statusSchema(db.status.find_one({"_id": ObjectId(id)}))

@router.put("/update/{id}" , response_model=Status)
async def update_status(id,update_status: Status, token = Depends(isAdmin)):
    update_data = {
        k: v for k, v in update_status.model_dump(exclude_unset=True).items()
        if v not in [None ,  ""  , "string" , 0]  
    }
    
    try:
        db.status.update_one({"_id": ObjectId(id)}, {"$set":update_data })
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El estado no existe")
    
    return statusSchema(db.status.find_one({"_id": ObjectId(id)}))

@router.delete("/delete/{id}")
async def delete_status(id, token = Depends(isAdmin)):
    found = db.status.find_one({"_id": ObjectId(id)}) 
    if not found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El estado no existe")
  