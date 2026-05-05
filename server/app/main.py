from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.mongo import close_client
from app.routers.chat import router as chat_router
from app.routers.evaluations import router as evaluations_router
from app.routers.learning_paths import router as learning_paths_router
from app.routers.notifications import router as notifications_router
from app.routers.observability import router as observability_router
from app.routers.profile import router as profile_router
from app.routers.resources import router as resources_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    await close_client()


app = FastAPI(title="CS Buddy Backend", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api/v1")
app.include_router(evaluations_router, prefix="/api/v1")
app.include_router(learning_paths_router, prefix="/api/v1")
app.include_router(notifications_router, prefix="/api/v1")
app.include_router(observability_router, prefix="/api/v1")
app.include_router(profile_router, prefix="/api/v1")
app.include_router(resources_router, prefix="/api/v1")


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok", "message": "服务运行正常"}
