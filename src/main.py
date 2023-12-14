from fastapi import FastAPI
import uvicorn
from starlette.middleware import Middleware

from src.apis.routers import main_router
from src.middlewares import EnsureSessionIDMiddleware
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(middleware=[Middleware(EnsureSessionIDMiddleware)])

origins = [
    "http://localhost:63342",
    "http://localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(main_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", log_level="info")
