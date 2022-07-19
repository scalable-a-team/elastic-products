#base directory for database engine to live

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import *




Engine = create_engine(POSTGRES_DATABASE)
Session = sessionmaker(bind=Engine)

Base = declarative_base()