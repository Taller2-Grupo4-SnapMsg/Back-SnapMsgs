# queries.py
"""
Module dedicated to the queries that the repository might need.
"""
from sqlalchemy.exc import IntegrityError
from repository.tables.tables import User
from repository.tables.tables import Following

#from repository.errors import UsernameAlreadyExists, EmailAlreadyExists
#from repository.errors import RelationAlreadyExists


def get_user_by_id(session, user_id):
    """
    Searches for a user by its id.
    """
    return session.query(User).filter(User.id == user_id).first()


def get_user_by_username(session, username):
    """
    Searches for a user by its username.
    """
    return session.query(User).filter(User.username == username).first()


def get_user_by_mail(session, mail):
    """
    Searches for a user by its mail.
    """
    return session.query(User).filter(User.email == mail).first()


def create_user(session, email, password, username, data):
    """
    Inserts a new user to the users table.
    :param: session: the session to use
    :param: username: the username of the user
    :param: surname: the surname of the user
    :param: name: the name of the user
    :param: password: the password of the user (already hashed)
    :param: email: the email of the user
    :param: date_of_birth: the date of birth of the user
    :returns: the user created or None if it fails
    """
    user = User(
        username=username,
        surname=data["surname"],
        name=data["name"],
        password=password,
        email=email,
        date_of_birth=data["date_of_birth"],
        bio=data["bio"],
        avatar=data["avatar"],
        admin=False,
    )
    try:
        session.add(user)
        session.commit()
        return user
    except IntegrityError as error:
        session.rollback()
        if "username" in str(error.orig):
            raise UsernameAlreadyExists() from error
        # if it's not the username, it's the email, there is no other unique fields
        raise EmailAlreadyExists() from error


def update_user_password(session, user_id, new_password):
    """
    Changes the information of the user with new_data
    :param: session: the session to use
    :param: user_id: the id of the user to change
    :param: new_data: the new data to change
    :returns: the user updated or None if it fails
    """
    user = session.query(User).filter(User.id == user_id).first()
    if user:
        setattr(user, "password", new_password)
        session.commit()
        return user
    return None


def delete_user(session, user_id):
    """
    Deletes the user with the given id.
    :param: session: the session to use
    :param: user_id: the id of the user to delete
    :returns: True if it found and deleted the user, false if it didn't
    """
    user = session.query(User).filter(User.id == user_id).first()
    if user:
        session.delete(user)
        session.commit()
        return True
    return False


# to do: maybe delete this?
def get_id_by_username(session, username):
    """
    Queries the database for the id of the user with the given username.
    """
    return session.query(User).filter(User.username == username).first().id


def update_user_admin(session, user_id, new_admin_status):
    """
    Changes the admin status of the user with the given id.
    """
    user = session.query(User).filter(User.id == user_id).first()
    if user:
        setattr(user, "admin", new_admin_status)
        session.commit()
        return user
    return None


def create_follow(session, username, username_to_follow):
    """
    Creates a follow relationship between two users.
    """
    user = get_user_by_username(session, username)
    user_to_follow = get_user_by_username(session, username_to_follow)
    if user and user_to_follow:
        try:
            following = Following(user.id, user_to_follow.id)
            session.add(following)
            session.commit()
        except IntegrityError as error:
            session.rollback()
            raise RelationAlreadyExists() from error
        return following
    return None


def get_followers(session, user_id):
    """
    Returns a list of the followers of the user with the given username.
    """
    users = session.query(Following).filter(Following.following_id == user_id).all()
    return [
        session.query(User).filter(User.id == user.user_id).first() for user in users
    ]


def get_following(session, user_id):
    """
    Returns a list of the users that the user with the given username is following.
    """
    users = session.query(Following).filter(Following.user_id == user_id).all()
    return [
        session.query(User).filter(User.id == user.following_id).first()
        for user in users
    ]


def get_following_relations(session):
    """
    Returns a list of all the following relations.
    """
    return session.query(Following).all()


def get_following_count(session, user_id):
    """
    Returns the number of users that the user with the given username is following.
    """
    return session.query(Following).filter(Following.user_id == user_id).count()


def get_followers_count(session, user_id):
    """
    Returns the number of followers of the user with the given username.
    """
    return session.query(Following).filter(Following.following_id == user_id).count()


def remove_follow(session, user_id, user_id_to_unfollow):
    """
    Removes the folowing relation between the two users.
    """
    following = (
        session.query(Following)
        .filter(Following.user_id == user_id)
        .filter(Following.following_id == user_id_to_unfollow)
        .first()
    )
    if following:
        session.delete(following)
        session.commit()
        return
    raise KeyError("The relation doesn't exist")


def update_user_bio(session, user_id, new_bio):
    """
    Changes the bio of the user with the given id.
    """
    user = session.query(User).filter(User.id == user_id).first()
    if user:
        setattr(user, "bio", new_bio)
        session.commit()
        return user
    return None


def update_user_name(session, user_id, new_name):
    """
    Changes the name of the user with the given id.
    """
    user = session.query(User).filter(User.id == user_id).first()
    if user:
        setattr(user, "name", new_name)
        session.commit()
        return user
    return None


def update_user_date_of_birth(session, user_id, new_date_of_birth):
    """
    Changes the date_of_birth of the user with the given id.
    """
    user = session.query(User).filter(User.id == user_id).first()
    if user:
        setattr(user, "date_of_birth", new_date_of_birth)
        session.commit()
        return user
    return None


def update_user_last_name(session, user_id, new_last_name):
    """
    Changes the last name of the user with the given id.
    """
    user = session.query(User).filter(User.id == user_id).first()
    if user:
        setattr(user, "surname", new_last_name)
        session.commit()
        return user
    return None


def update_user_avatar(session, user_id, new_avatar):
    """
    Changes the avatar of the user with the given id.
    """
    user = session.query(User).filter(User.id == user_id).first()
    if user:
        setattr(user, "avatar", new_avatar)
        session.commit()
        return user
    return None


def get_all_users(session):
    """
    Query mostly for testing, it retrieves all the users of the database.
    """
    return session.query(User).all()
