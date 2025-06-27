# from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine


#DATABASE_URL = "sqlite+aiosqlite:///./taskapp.db"
# DATABASE_URL = "postgresql+asyncpg://postgres:niraj@localhost:5433/TodoApplicationDatabase"
#For not sync

# engine = create_async_engine(DATABASE_URL, echo=True)
# AsyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_= AsyncSession)



# # initialize database for async
# async def init_db():
#     async with engine.begin() as connection:
#         await connection.run_sync(Base.metadata.create_all)
        
# # create Dependecies , fetch the data and close the connection        
# async def get_db():
#     async with AsyncSessionLocal() as db:    
#         try: 
#             yield db # yield means return
#         finally:
#             #db.close
#             await db.close()   
DATABASE_URL = "postgresql://postgres:password@host.docker.internal:5433/TodoApplicationDatabase"
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()  