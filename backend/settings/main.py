import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth.router import router as router_auth
from magazines.router import router as router_magazines
from articles.router import router as router_articles

from settings.database import async_session_maker

from services.autostart.initial_data import InitializationData

app = FastAPI(
    title=" ComeBack Agency",
    description="API for ComeBack Agency",
)

current_dir = os.path.join(os.path.dirname(__file__))

# Authorizations
app.include_router(
    router_auth,
    prefix="/auth",
    tags=["Auth"],
)
# Magazines
app.include_router(
    router_magazines,
    prefix="/magazines",
    tags=["Magazines"],
)
# Articles
app.include_router(
    router_articles,
    prefix="/articles",
    tags=["Articles"],
)


@app.on_event("startup")
async def startup_event():
    async with async_session_maker() as session:
        init_data = InitializationData(session)
        await init_data.start_app()


origins = ["*"]

# Настройки CORS и конфигурации
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["*"],
)
