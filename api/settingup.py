import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from decouple import config
from models import Base

SQLALCHEMY_DATABASE_URL = config('POSTGRES_URL')


engine = create_engine(config('POSTGRES_URL'), pool_size=3, max_overflow=0)

Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(engine)
 
