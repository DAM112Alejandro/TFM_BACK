from datetime import datetime,timedelta, timezone
from typing import Annotated
from bson import ObjectId
from fastapi import Depends, HTTPException, APIRouter ,status
from pydantic import BaseModel
from passlib.context import CryptContext 
from fastapi.security import HTTPBearer, OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from db.client import db



from db.models.users import Users
from config import SECRET_KEY , ALGORITHM , ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter( prefix="/auth", tags=["auth"])

brcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")   
#Solo auth con jwt
#auth =  HTTPBearer()

class CreateUserRequest(BaseModel):
    username: str
    email : str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    
class CurrentUser(BaseModel):
    username: str
    email: str
    rolDescription: str
    rolId: str
    id: str
    
def authenticateUser(email: str, password: str):
    user = db.users.find_one({"email": email})
    if not user:
        return False
    if not brcrypt_context.verify(password, user["password"]):
        return False
    return user

def isRegistered(email: str):
    user = db.users.find_one({"email": email})
    if user: return False
    else: return True

def create_token(username: str, id: ObjectId, expires_delta: timedelta):
    encode  = { 'sub': username , 'id': str(id) }
    expire = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expire})
    return jwt.encode(encode, SECRET_KEY, ALGORITHM)

async def isLogged(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get("id")
        if id is None:
            raise credentials_exception
        token_data = db.users.find_one({"_id": ObjectId(id)})
        if token_data is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return token_data

async def get_current_user(token: str = Depends(oauth2_scheme)) -> CurrentUser:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("id")
        if id is None:
            raise credentials_exception
        token_data = db.users.find_one({"_id": ObjectId(user_id)})
        if token_data is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    userRol = await getRoleById(token_data["rol_id"])
    
    return CurrentUser(username=token_data["username"], email=token_data["email"], rolDescription = userRol ,rolId = token_data["rol_id"] , id = user_id)



async def isAdmin(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get("id")
        if id is None:
            raise credentials_exception
        token_data = db.users.find_one({"_id": ObjectId(id)})
        if token_data is None:
            raise credentials_exception
        if token_data.get("rol_id") != getRole("ADMIN"):
            raise credentials_exception
    except JWTError:    
        raise credentials_exception
    return token_data    


def hashPassword(password: str):
    return brcrypt_context.hash(password)

def getRole(role: str):
    found = db.roles.find_one({"description": role})
    if not found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El rol no existe")
    return str(found["_id"])

async def getRoleById(id):
    found = db.roles.find_one({"_id": ObjectId(id)})
    if not found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El rol no existe")
    return found["description"]

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: CreateUserRequest):
    newUser =  isRegistered(user.email)
    if(not newUser):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exist")
        
    else:
        create_user = Users(
            username = user.username,
            email = user.email,
            password =  brcrypt_context.hash(user.password),
            rol_id = getRole("TECNICO"),
        )
        user_dict = create_user.model_dump()
        db.users.insert_one(user_dict)
        return {"success": "User created successfully"}
    
@router.post("/login")
async def login(form_data: Annotated[OAuth2PasswordRequestForm ,Depends()]):
    user = authenticateUser(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
        
    token = create_token(user['email'], user['_id'] , timedelta(minutes=float(ACCESS_TOKEN_EXPIRE_MINUTES)))
    return {"success": True, "access_token": token}

@router.get("/user")
def getCurrentUser(current_user: CurrentUser = Depends(get_current_user)):
    return current_user
    