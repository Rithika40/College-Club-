from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from backend.database import Base, engine
from backend.routers import router
from backend.seed import seed_if_empty
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

FRONTEND = Path(__file__).resolve().parent.parent / "frontend"

app = FastAPI(title="College Club Management System", version="1.0")
app.include_router(router, prefix="/api")


@app.exception_handler(RequestValidationError)
async def request_validation_handler(_request: Request, exc: RequestValidationError):
    messages = []
    for err in exc.errors():
        loc = " ".join(str(x) for x in err.get("loc", []) if x != "body")
        messages.append(f"{loc}: {err.get('msg', 'Invalid input')}".strip(": "))
    return JSONResponse(status_code=422, content={"detail": "; ".join(messages) or "Invalid input."})


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    seed_if_empty()


@app.get("/api/health")
def health():
    return {"status": "ok"}


if FRONTEND.exists():
    app.mount("/static", StaticFiles(directory=FRONTEND), name="static")


@app.get("/")
def root():
    return FileResponse(FRONTEND / "index.html")


@app.get("/app")
def app_page():
    return FileResponse(FRONTEND / "app.html")
