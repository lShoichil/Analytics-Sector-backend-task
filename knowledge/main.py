from fastapi import FastAPI
from fastapi_pagination import add_pagination

from . import models
from .database import engine
from .routers import user

app = FastAPI()

models.Base.metadata.create_all(engine)

app.include_router(user.router)

add_pagination(app)

