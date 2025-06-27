from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import Annotated
from sqlalchemy.orm import Session
from ..models import Users
from starlette import status
from passlib.context import CryptContext
# from ..db import AsyncSessionLocal
from ..db import SessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer # OAuth2PasswordBearer -checks bearer token
from sqlalchemy.future import select
from jose import jwt, JWTError
from datetime import timedelta, datetime, timezone
from fastapi.templating import Jinja2Templates



router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

SECRET_KEY = '5e7b189afb0e38f4ddf82be00b8166092bd4f2f23f292369107d74d7de7c76ba'
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token') # to verify bearer token from token

class Token(BaseModel):
    access_token: str
    token_type: str
    
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]  
templates = Jinja2Templates(directory="Todo/templates")

### Pages ###

@router.get("/login-page")
def render_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/register-page")
def render_register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

  
# create Dependecies , fetch the data and close the connection        
# async def get_db():
#     async with AsyncSessionLocal() as db:    
#         try: 
#             yield db # yield means return
#         finally:
#             #db.close
#             await db.close() 

# # authenticate user            
# async def authenticate_user(username: str, password: str, db):
#     #user = db.query(Users).filter(Users.username == username).first()
#     result = await db.execute(select(Users).where(Users.username == username))
#     user = result.scalars().first()
#     if not user:
#         return False
#     if not bcrypt_context.verify(password, user.hashed_password):
#         return False
#     return user 

# # authenticate token
# def create_access_token(username: str, user_id: int, role:str, expires_delta: timedelta):
#     encode = {'sub': username, 'id': user_id, 'role':role}
#     expires = datetime.now(timezone.utc) + expires_delta
#     encode.update({'exp': expires})
#     return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)  

# # To decode token- verify token is fake or real
# async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get('sub')
#         user_id: int = payload.get('id')
#         user_role: str = payload.get('role')
#         if username is None or user_id is None:
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
#                                 detail='Could not validate user.')
#         return {'username': username, 'id': user_id, 'user_role': user_role}
#     except JWTError:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
#                             detail='Could not validate user.')         

class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str
    phone_number: str


# @router.post("/", status_code=status.HTTP_201_CREATED)
# async def create_user( create_user_request : CreateUserRequest, db: AsyncSession = Depends(get_db)):
#     create_user_model = Users(
#         email=create_user_request.email,
#         username=create_user_request.username,
#         first_name=create_user_request.first_name,
#         last_name=create_user_request.last_name,
#         role=create_user_request.role,
#         hashed_password=bcrypt_context.hash(create_user_request.password),
#         is_active=True,
#         phone_number=create_user_request.phone_number
#     )

#     db.add(create_user_model)
#     await db.commit()
#     await db.refresh(create_user_model)


# # route or getting token    
# @router.post("/token", response_model=Token)
# async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
#                                  db: AsyncSession = Depends(get_db)):

#     user = await authenticate_user(form_data.username, form_data.password, db)
#     if not user:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
#                             detail='Could not validate user.')
#     token = create_access_token(user.username, user.id, user.role, timedelta(minutes=20))    
#     return {'access_token': token, 'token_type': 'bearer'}


def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id, 'role': role}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        user_role: str = payload.get('role')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not validate user.')
        return {'username': username, 'id': user_id, 'user_role': user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency,
                      create_user_request: CreateUserRequest):
    create_user_model = Users(
        email=create_user_request.email,
        username=create_user_request.username,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        role=create_user_request.role,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        is_active=True,
        phone_number=create_user_request.phone_number
    )

    db.add(create_user_model)
    db.commit()


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')
    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=20))

    return {'access_token': token, 'token_type': 'bearer'}