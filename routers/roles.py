from fastapi import APIRouter , Depends , status , HTTPException
from bson import ObjectId
from db.models.roles import Roles
from db.schemas.rolesSchema import roleSchema , roleListSchema
from db.client import db
from auth.auth import isLogged, isAdmin


router = APIRouter(
    prefix="/roles",
    tags=["roles"],
    responses={ status.HTTP_404_NOT_FOUND: { "description": "Roles no encontrado" }},
)

@router.get("")
async def get_roles(token = Depends(isAdmin)):
    return roleListSchema(db.roles.find())

@router.get("/{id}")
async def get_role_by_id(id: str,token = Depends(isLogged)):
    found = db.roles.find_one({"_id": ObjectId(id)})
    if not found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El rol no existe")
    return roleSchema(found)

@router.post("/add", response_model=Roles)
async def add_role(new_role: Roles, token = Depends(isAdmin)):
    if db.roles.find_one({ 'description': new_role.description }):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El rol ya existe")
    
    roleDict = dict(new_role)
    id = db.roles.insert_one(roleDict).inserted_id
    
    return roleSchema(db.roles.find_one({"_id": ObjectId(id)}))

@router.put("/update/{id}" , response_model=Roles)
async def update_role(update_role: Roles, id , token = Depends(isAdmin)):
    update_data = {
        k: v for k, v in update_role.model_dump(exclude_unset=True).items()
        if v not in [None ,  ""  , "string" , 0]  
    }
    
    try:
        db.roles.update_one({"_id": ObjectId(id)}, {"$set":update_data })
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El rol no existe")
    
    return roleSchema(db.roles.find_one({"_id": ObjectId(id)}))

@router.delete("/delete/{id}")
async def delete_role(id , token = Depends(isAdmin)):
    found = db.roles.find_one({"_id": ObjectId(id)}) 
    if not found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El rol no existe")
  