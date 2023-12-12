from fastapi import FastAPI
import uvicorn
from starlette.middleware import Middleware

from src.apis.routers import main_router
from src.middlewares import EnsureSessionIDMiddleware

app = FastAPI(middleware=[Middleware(EnsureSessionIDMiddleware)])

app.include_router(main_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", log_level="info")
