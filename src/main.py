from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.infrastructure.database import init_db, SessionLocal
from src.infrastructure.seed import seed_database_if_empty
from src.api.routes import router as equipment_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Inicializace DB a případný seed
    init_db()
    if settings.SEED_ON_STARTUP:
        db = SessionLocal()
        try:
            seeded_count = seed_database_if_empty(db)
            if seeded_count > 0:
                print(f"[Seed] Vloženo {seeded_count} výchozích kusů vybavení.")
        finally:
            db.close()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Informační systém půjčovny vybavení Hory a voda (PPRO Zadání D)",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Zákaz ukládání do mezipaměti prohlížeče pro statické soubory během vývoje
@app.middleware("http")
async def add_no_cache_headers(request: Request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/static") or request.url.path == "/":
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

# API routery
app.include_router(equipment_router)

# Statické soubory pro Pultový dashboard
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/", include_in_schema=False)
    async def serve_index():
        return FileResponse(static_dir / "index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
