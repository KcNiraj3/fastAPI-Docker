# import datetime
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware

# from fastapi.responses import HTMLResponse
# from fastapi.staticfiles import StaticFiles
from .db import engine
from .routers import auth, task, admin, users
from .models import Base
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse



app = FastAPI() 
Base.metadata.create_all(bind=engine)


app.mount("/static", StaticFiles(directory="Todo/static"), name="static")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    #ALLOW_METHODS=["GET"]
)

@app.get("/")
def test(request: Request):
    return RedirectResponse(url='/todos/todo-page', status_code=status.HTTP_302_FOUND)


@app.get("/healthy")
def health_check():
    return {'status': 'Healthy'}


app.include_router(auth.router)
app.include_router(task.router)
app.include_router(admin.router)
app.include_router(users.router)










