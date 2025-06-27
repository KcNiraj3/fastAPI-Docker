from fastapi import APIRouter, Path
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
# from ..db  import get_db
from ..models import Task
from fastapi import HTTPException
from ..requests_models import taskRequest
from ..response_models import TaskResponse
import datetime
import asyncio
from typing import Annotated, List
from starlette import status
from .auth import get_current_user
from sqlalchemy.orm import Session
from ..db import SessionLocal

#router = APIRouter(prefix="/api")
router = APIRouter(prefix='/admin',
    tags=['admin'])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
        
# dependency for validating tokens
user_dependency = Annotated[dict, Depends(get_current_user)]
db_dependency = Annotated[Session, Depends(get_db)]

# @router.get("/todo", status_code=status.HTTP_200_OK)
# async def read_all(user: user_dependency, session: AsyncSession = Depends(get_db)):
#     if user is None or user.get('user_role') != 'admin':
#         raise HTTPException(status_code=401, detail='Authentication Failed')
#     result = await session.execute(select(Task))
#     tasks = result.scalars().all()
#     return tasks


# @router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_todo(user: user_dependency, db: AsyncSession = Depends(get_db), todo_id: int = Path(gt=0)):
#     if user is None or user.get('user_role') != 'admin':
#         raise HTTPException(status_code=401, detail='Authentication Failed')
#     todo_model = await db.execute(select(Task).where(Task.id == todo_id))
#     task = todo_model.scalar_one_or_none()
#     if task is None:
#         raise HTTPException(status_code=404, detail='Todo not found.')
#     await db.delete(task)
#     await db.commit()
#     return {"message":"Task deleted sucessfully"}

@router.get("/todo", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')
    return db.query(Task).all()


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')
    todo_model = db.query(Task).filter(Task.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found.')
    db.query(Task).filter(Task.id == todo_id).delete()
    db.commit()