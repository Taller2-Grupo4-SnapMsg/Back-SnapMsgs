# We connect to the database using the ORM defined in tables.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from repository.tables.tables import Base, Posts, Likes

# CREATING CONNECTIONS TO DATA BASES
engine_posts = create_engine(os.environ.get("DB_URI"))

# Create the tables in the database
Base.metadata.create_all(engine_posts)

# Session is the handle of the database
Session = sessionmaker(bind=engine_posts)
session = Session()
TIMEOUT = 60

def get_post_by_user_email(session, user_email):
    """
    Searches for a post by the email of the user
    """
    return session.query(Posts).filter(Posts.email_user == user_email).first()


