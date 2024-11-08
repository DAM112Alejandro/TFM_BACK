from fastapi import FastAPI
from routers import jobs , roles , status , workTypes , users 
from auth import auth
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],  
)

app.include_router(jobs.router)
app.include_router(roles.router)
app.include_router(status.router)
app.include_router(workTypes.router)
app.include_router(users.router)
app.include_router(auth.router)