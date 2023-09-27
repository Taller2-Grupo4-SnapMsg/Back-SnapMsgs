# We connect to the database using the ORM defined in tables.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from repository.tables.tables import LocalBase, RemoteBase, Posts, Likes

# Creating engines
engine_posts = create_engine(os.environ.get("DB_URI"))
engine_users = create_engine(os.environ.get("DB_USERS_URI"))

# Creating the tables in the database
LocalBase.metadata.create_all(engine_posts)
RemoteBase.prepare(engine_users, reflect=True)
UserRemote = RemoteBase.classes.users

# Session is the handle of the database
Session = sessionmaker(bind=engine_posts)
session = Session()
TIMEOUT = 60

def get_post_by_user_email(session, user_email):
    """
    Searches for a post by the email of the user
    """
    return session.query(Posts).filter(Posts.email_user == user_email).first()


