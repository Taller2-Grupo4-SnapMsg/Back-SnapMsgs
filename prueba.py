from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from repository.queries.queries import UserRemote  # Import the User class

# Create an engine and session
engine = create_engine(
    "postgresql://cwfvbvxl:jtsNDRjbVqGeBgYcYvxGps3LLlX_t-P5@berry.db.elephantsql.com:5432/cwfvbvxl"
)
Session = sessionmaker(bind=engine)
session = Session()

# Fetch a user and print their username
user = session.query(UserRemote).first()
print(user.username)
