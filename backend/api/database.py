# import databases
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from starlette.config import Config
from starlette.datastructures import Secret

config = Config(".env")

if config("production", cast=bool, default=False):
    DATABASE_URI = str(config("DATABASE_URI", cast=Secret))
    engine = create_engine(DATABASE_URI)
else:
    if config("TEST", cast=bool, default=False):
        DATABASE_URL = "sqlite:///./test.db"
    else:
        DATABASE_URL = "sqlite:///./reflect.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
