from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

import app.router as router
from app.utils import settings
from app.utils.logger import logger

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.fastapi.allow_origins,
    allow_credentials=settings.fastapi.allow_credentials,
    allow_methods=settings.fastapi.allow_methods,
    allow_headers=settings.fastapi.allow_headers,
)
app.include_router(router.default_router)
app.include_router(router.settings_router)
app.mount("/data/이지원", StaticFiles(directory="data/이지원"), name="data/이지원")
logger.debug("Initialized FastAPI App")

mount_chainlit(app=app, target="cl_app.py", path="/chainlit")
logger.debug("Initialized chainlit")
