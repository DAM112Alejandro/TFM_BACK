from fastapi import APIRouter , Depends , status , HTTPException
from bson import ObjectId
from db.models.users import Users 
from db.schemas.usersSchema import userSchema , userListSchema
from db.client import db
from auth.auth import isAdmin , isLogged


router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={ status.HTTP_404_NOT_FOUND: { "description": "Usuario no encontrado" }},
)

@router.get("")
async def get_users (token = Depends(isAdmin)):
    return userListSchema(db.users.find())

@router.get("/user/{id}")
async def get_users_by_id(id, token = Depends(isLogged)):
    found = db.users.find_one({"_id": ObjectId(id)})
    if not found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El usuario no existe")
    return userSchema(found)

@router.get("/tecnicos")
async def get_tecnicos(token = Depends(isAdmin)):
    tec_users = []

    role = db.roles.find_one({"description": "TECNICO"})
    if not role:
        raise HTTPException(status_code=404, detail="Rol 'TECNICO' no encontrado")
    users = db.users.find()
    for user in users:
        if user.get("rol_id") and ObjectId(user["rol_id"])== role["_id"]:
            tec_users.append(user)

    if not tec_users:
        raise HTTPException(status_code=404, detail="No se encontraron usuarios con el rol 'TECNICO'")

    return userListSchema(tec_users)

@router.put("/edit/{id}", response_model=Users)
async def edit_user(id, update_users: Users ,token=Depends(isAdmin)):
    update_data = {
        k: v for k, v in update_users.model_dump(exclude_unset=True).items()
        if v not in [None ,  ""  , "string" , 0]  
    }
    try:
        db.users.find_one_and_update({"_id": ObjectId(id)}, {"$set": update_data })
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El usuario no existe")
    
    return userSchema(db.users.find_one({"_id": ObjectId(id)}))


@router.delete("/delete/{id}")
async def delete_users(id , token = Depends(isAdmin)):
    found = db.users.find_one_and_delete({"_id": ObjectId(id)}) 
    if not found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El usuario no existe")
  