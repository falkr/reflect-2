# import databases
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from starlette.config import Config
from starlette.datastructures import Secret

config = Config(".env")

if config("production", cast=bool, default=False):
    postgres_user = str(config("POSTGRES_USER", cast=Secret))
    postgres_pass = str(config("POSTGRES_PASSWORD", cast=Secret))
    DATABASE_URL = (
        f"postgresql://{postgres_user}:{postgres_pass}@reflect_v2_db_1:5432/reflect"
    )
    # database = databases.Database(DATABASE_URL)
    engine = create_engine(DATABASE_URL)
else:
    if config("TEST", cast=bool, default=False):
        DATABASE_URL = "sqlite:///./test.db"
    else:
        DATABASE_URL = "sqlite:///./reflect.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
