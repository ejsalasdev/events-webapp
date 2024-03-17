from fastapi import FastAPI, Request
from models import models
from config.database import engine
from routes import admin, users

from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")


app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(admin.router)
app.include_router(users.router)


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
