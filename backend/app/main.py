from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.api import resume, module, field, export, github


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Find Job API",
    version="1.0.0",
    lifespan=lifespan,
)

origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_prefix = settings.API_PREFIX.strip().rstrip("/")
app.include_router(resume.router, prefix=api_prefix)
app.include_router(module.router, prefix=api_prefix)
app.include_router(field.router, prefix=api_prefix)
app.include_router(export.router, prefix=api_prefix)
app.include_router(github.router, prefix=api_prefix)


@app.get("/health")
async def health():
    return {"status": "ok"}
