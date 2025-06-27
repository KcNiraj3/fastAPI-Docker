# from fastapi import APIRouter, Path
# from sqlalchemy.future import select
# from sqlalchemy.ext.asyncio import AsyncSession
# from fastapi import Depends
# from ..db  import get_db
# from ..models import Task
# from fastapi import HTTPException
# from ..requests_models import taskRequest
# from ..response_models import TaskResponse
# import datetime
# import asyncio
# from typing import Annotated, List
# from starlette import status
# from .auth import get_current_user

# #router = APIRouter(prefix="/api")
# router = APIRouter()

# # dependency for validating tokens
# user_dependency = Annotated[dict, Depends(get_current_user)]

# # create more than one task
# @router.post("/tasks/", response_model=list[taskRequest], status_code = status.HTTP_201_CREATED)  
# async def create_tasks(user:user_dependency, tasks:list[taskRequest], db: AsyncSession = Depends(get_db)):
#     task_obj = [] # create task obj for async
#     if user is None:
#         raise HTTPException(status_code=401, detail='Authenticated Failed')
#     for db_task in tasks:
#         db_task = Task(**db_task.dict(), owner_id=user.get('id'))
#         db.add(db_task)
#         await db.commit()
#         await db.refresh(db_task)
#         task_obj.append(db_task) # add in database
#     return task_obj   


# #To get all tasks
# @router.get("/tasks/all", status_code = status.HTTP_200_OK) 
# #@router.get("/tasks/all", response_model=List[TaskResponse]) 
# async def getAll_tasks(user:user_dependency, session: AsyncSession = Depends(get_db)):
#     if user is None:
#         raise HTTPException(status_code=401, detail='Authenticated Failed')
#     #tasks = await db.query(Task).all() #select * from tasks
#     result = await session.execute(select(Task).where(Task.owner_id == user.get("id")))
#     tasks = result.scalars().all() # convert into data (reference) from object , if we do not put scalar it will return only object
#     if not tasks:
#         return {"message":"Tasks not found"}
#     return [i for i in tasks]


# @router.get("/tasks/{task_id}", response_model=TaskResponse, status_code=status.HTTP_200_OK)  
# async def get_tasks(user:user_dependency, task_id:int = Path(gt=0), session: AsyncSession = Depends(get_db)): # Depends is dependency injection
#     if user is None:
#         raise HTTPException(status_code=401, detail='Authenticated Failed')
#     _start = datetime.datetime.now()
#     query1 = session.execute(
#         select(Task).where(Task.id == task_id).where(Task.owner_id == user.get('id'))
#     )
    
#     query2 = session.execute(
#         select(Task)
#     )
    
#     # asyncio.gather starts both queries at the same time
#     # saves time compared to awaiting them one by one
#     query1, query2 = await asyncio.gather(
#         query1,
#         query2
#     )
#     task1 = query1.scalar()
#     print(f"\n\n{query1}, {task1}")
#     _end = datetime.datetime.now()
#     print(f"\n\ntime_taken: {_end-_start}\n\n")
#     if not task1:
#         raise HTTPException(status_code=404, detail="Task not found")
#     print(task1)
#     return task1



# @router.put("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)  
# async def edit_tasks(user:user_dependency, task:taskRequest, task_id:int = Path(gt=0) ,db: AsyncSession = Depends(get_db)):
#     if user is None:
#         raise HTTPException(status_code=401, detail='Authenticated Failed')
#     result = await db.execute(select(Task).where(Task.id == task_id).where(Task.owner_id == user.get('id')))
#     _task = result.scalar_one_or_none()
#     #if _task in None:
#     if not _task:
#         raise HTTPException(status_code=404, detail='Tasks not found')
#     _task.title = task.title
#     _task.description = task.description
#     _task.priority = task.priority
#     _task.is_completed = task.is_completed
#     db.add(_task)
#     await db.commit()
#     await db.refresh(_task)
#     return _task


# @router.delete("/tasks/{task_id}")  
# async def delete_tasks(user:user_dependency, task_id:int, task:taskRequest, db: AsyncSession = Depends(get_db)):
#     if user is None:
#         raise HTTPException(status_code=401, detail='Authenticated Failed')
#     result = await db.execute(select(Task).where(Task.id == task_id).where(Task.owner_id == user.get('id')))
#     _task =  result.scalar_one_or_none()
#     if not _task:
#         raise HTTPException(status_code=404, detail="Task not found")

#     await db.delete(_task)
#     await db.commit()
#     return {"message":"Task deleted sucessfully"}

from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status
from ..models import Task
from ..db import SessionLocal
from .auth import get_current_user
from fastapi import APIRouter, Depends, HTTPException, Path, Request, status
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional

router = APIRouter( prefix='/todos',
    tags=['todos'])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
templates = Jinja2Templates(directory="Todo/templates")


class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    is_completed: Optional[bool]=False
  
    
def redirect_to_login():
    redirect_response = RedirectResponse(url="/auth/login-page", status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie(key="access_token")
    return redirect_response    


@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    return db.query(Task).filter(Task.owner_id == user.get('id')).all()


@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    todo_model = db.query(Task).filter(Task.id == todo_id)\
        .filter(Task.owner_id == user.get('id')).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail='Todo not found.')


@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, db: db_dependency,
                      todo_request: TodoRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    todo_model = Task(**todo_request.model_dump(), owner_id=user.get('id'))

    db.add(todo_model)
    db.commit()


@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency, db: db_dependency,
                      todo_request: TodoRequest,
                      todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    todo_model = db.query(Task).filter(Task.id == todo_id)\
        .filter(Task.owner_id == user.get('id')).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found.')

    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.is_completed = todo_request.is_completed

    db.add(todo_model)
    db.commit()


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    todo_model = db.query(Task).filter(Task.id == todo_id)\
        .filter(Task.owner_id == user.get('id')).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found.')
    db.query(Task).filter(Task.id == todo_id).filter(Task.owner_id == user.get('id')).delete()

    db.commit()
    
### Pages ###

@router.get("/todo-page")
async def render_todo_page(request: Request, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get('access_token'))

        if user is None:
            return redirect_to_login()

        todos = db.query(Task).filter(Task.owner_id == user.get("id")).all()

        return templates.TemplateResponse("todo.html", {"request": request, "todos": todos, "user": user})

    except:
        return redirect_to_login()    
    
@router.get('/add-todo-page')
async def render_todo_page(request: Request):
    try:
        user = await get_current_user(request.cookies.get('access_token'))

        if user is None:
            return redirect_to_login()

        return templates.TemplateResponse("add_todo.html", {"request": request, "user": user})

    except:
        return redirect_to_login()  
    
    
@router.get("/edit-todo-page/{todo_id}")
async def render_edit_todo_page(request: Request, todo_id: int, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get('access_token'))

        if user is None:
            return redirect_to_login()

        todo = db.query(Task).filter(Task.id == todo_id).first()

        return templates.TemplateResponse("edit-todo.html", {"request": request, "todo": todo, "user": user})

    except:
        return redirect_to_login()      