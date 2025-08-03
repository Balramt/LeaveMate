import os
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from app.auth import router as auth_router
from app.routes.leave import router as leave_router
from app.routes.admin_leave import router as admin_router
from app.db import engine, Base
import logging
import traceback

app = FastAPI()

@app.exception_handler(Exception)
async def log_exception(request, exc):
    print("💥 Exception:", repr(exc))
    traceback.print_exc()
    return HTMLResponse("Internal Server Error", status_code=500)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app.add_middleware(SessionMiddleware, secret_key="super-secret-key")
#app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# Create DB tables
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(auth_router)
app.include_router(leave_router)
app.include_router(admin_router)
