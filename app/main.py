from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from router import default_router, settings_router
from utils import logger, settings

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.fastapi.allow_origins,
    allow_credentials=settings.fastapi.allow_credentials,
    allow_methods=settings.fastapi.allow_methods,
    allow_headers=settings.fastapi.allow_headers,
)
app.include_router(default_router)
app.include_router(settings_router)
app.mount("/data/이지원", StaticFiles(directory="data/이지원"), name="data/이지원")
logger.debug("Initialized FastAPI App")
