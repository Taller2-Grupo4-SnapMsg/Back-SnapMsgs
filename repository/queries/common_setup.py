# pylint: disable=R0801
"""
Archivo con configuracion de la base de datos
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# pylint: disable=C0114, W0401, W0614, E0401
from repository.tables.users import Base

# Creating engines
engine_posts = create_engine(os.environ.get("DB_URI"))

# Creating the tables in the database
Base.metadata.create_all(engine_posts)

# Session is the handle of the database
Session = sessionmaker(bind=engine_posts)
session = Session()
TIMEOUT = 60
