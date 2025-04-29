from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.routers import bodypart
from app.database import Base, engine
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
from fastapi.responses import JSONResponse
from fastapi.requests import Request


settings = get_settings()

app = FastAPI(title="Supplement Recommendation API")
openai_api_key = settings.openai_api_key

@app.get("/")
def root():
    return {"message": "API 서버 정상 작동"}

@app.exception_handler(Exception)
async def internal_exception_handler(request: Request, exc: Exception):
    logging.exception("Unhandled exception occurred:")
    return JSONResponse(status_code=500, content={"detail": str(exc)})

Base.metadata.create_all(bind=engine)

# CORS
origins = [o.strip() for o in settings.allowed_origins.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router 등록
app.include_router(bodypart.router)

# main.py(디버깅용 임시)
if __name__ == "__main__":
    print("routes =", [route.path for route in app.routes])

@app.on_event("startup")
async def _show_routes() -> None:
    print("registered routes =", [r.path for r in app.routes])