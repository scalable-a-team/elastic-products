#base directory for database engine to live

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import *
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor


Psycopg2Instrumentor().instrument()


Engine = create_engine(POSTGRES_DATABASE)
Session = sessionmaker(bind=Engine)

Base = declarative_base()


SQLAlchemyInstrumentor().instrument(engine=Engine)
