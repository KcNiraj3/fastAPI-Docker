

# from pydantic import BaseModel


# class TaskResponse(BaseModel):
#     id: int  #  If no value is provided, it will default to None
#     title:str = None
#     description:str = None
#     priority: int = None
#     is_completed: bool = None  
    
#     class Config:
#         orm_mode = True

from typing import Optional
from pydantic import BaseModel

class TaskResponse(BaseModel):
    id: Optional[int]
    title: Optional[str]
    description: Optional[str]
    priority: Optional[int]
    is_completed: Optional[bool]

    class Config:
        orm_mode = True
