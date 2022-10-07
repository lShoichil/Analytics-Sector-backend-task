from fastapi import FastAPI
from fastapi_pagination import add_pagination
from .routers import user

app = FastAPI()

app.include_router(user.router)

add_pagination(app)
