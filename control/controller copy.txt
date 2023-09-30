# controler.py

"""
This is the controller layer of the REST API for the login backend.
"""
import datetime
from pydantic import BaseModel

# Para permitir pegarle a la API desde localhost:
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from fastapi import Depends
from fastapi import Header
from service.user import User
from service.user import change_password as change_password_service
from service.user import change_bio as change_bio_service
from service.user import change_name as change_name_service
from service.user import change_date_of_birth as change_date_of_birth_service
from service.user import change_last_name as change_last_name_service
from service.user import change_avatar as change_avatar_service
from service.user import get_user_email as get_user_service
from service.user import get_user_password
from service.user import remove_user_email
from service.user import get_all_users as get_all_users_service
from service.user import get_user_username
from service.user import make_admin as make_admin_service
from service.user import remove_admin_status as remove_admin_service
from service.user import create_follow as create_follow_service
from service.user import (
    get_all_following_relations as get_all_following_relations_service,
)
from service.user import get_all_followers
from service.user import get_all_following
from service.user import get_followers_count as get_followers_count_service
from service.user import get_following_count as get_following_count_service
from service.user import remove_follow as remove_follow_service
from service.errors import UserNotFound
from service.errors import UsernameAlreadyRegistered, EmailAlreadyRegistered
from service.errors import UserCantFollowItself, FollowingRelationAlreadyExists
from control.auth import AuthHandler

USER_ALREADY_REGISTERED = 409
USER_NOT_FOUND = 404
USER_NOT_ADMIN = 400
PASSWORD_DOESNT_MATCH = 401

app = FastAPI()
auth_handler = AuthHandler()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Define a Pydantic model for the request body
class UserRegistration(BaseModel):
    """
    This class is a Pydantic model for the request body.
    """

    password: str
    email: str
    name: str
    last_name: str
    username: str
    date_of_birth: str


class UserResponse(BaseModel):
    """
    This class is a Pydantic model for the response body.
    """

    email: str
    name: str
    last_name: str
    username: str
    date_of_birth: str
    bio: str
    avatar: str

    # I disable it since it's a pydantic configuration
    # pylint: disable=too-few-public-methods
    class Config:
        """
        This is a pydantic configuration so I can cast
        orm_objects into pydantic models.
        """

        orm_mode = True
        from_attributes = True


def generate_response(user):
    """
    This function casts the orm_object into a pydantic model.
    (from data base object to json)
    """
    return UserResponse(
        email=user.email,
        name=user.name,
        last_name=user.surname,
        username=user.username,
        date_of_birth=str(user.date_of_birth),
        bio=user.bio,
        avatar=user.avatar,
    )


def generate_response_list(users):
    """
    This function casts the list of users into a list of pydantic models.
    """
    response = []
    for user in users:
        response.append(generate_response(user))
    return response


# Create a POST route
@app.post("/register", status_code=201)
def register_user(user_data: UserRegistration):
    """
    This function is the endpoint for user registration.
    """

    user = User()

    hashed_password = auth_handler.get_password_hash(user_data.password)
    user.set_password(hashed_password)

    user.set_email(user_data.email)
    user.set_name(user_data.name)
    user.set_surname(user_data.last_name)
    user.set_username(user_data.username)
    user.set_bio("")
    date_time = user_data.date_of_birth.split(" ")
    user.set_date_of_birth(
        datetime.datetime(int(date_time[0]), int(date_time[1]), int(date_time[2]))
    )
    user.set_admin(False)
    try:
        user.save()
        token = auth_handler.encode_token(user_data.email)
    except UsernameAlreadyRegistered as error:
        raise HTTPException(
            status_code=USER_ALREADY_REGISTERED, detail=str(error)
        ) from error
    except EmailAlreadyRegistered as error:
        raise HTTPException(
            status_code=USER_ALREADY_REGISTERED, detail=str(error)
        ) from error
    return {"message": "Registration successful", "token": token}


class UserLogIn(BaseModel):
    """
    This class is a Pydantic model for the request body.
    """

    email: str
    password: str


# Route to handle user login
@app.post("/login/", status_code=200)
def login(user_data: UserLogIn):
    """
    This function is the endpoint for the mobile front to log in an already existing user

    :param user: The user to login.
    :return: Status code with a JSON message.
    """
    try:
        hash_password = get_user_password(user_data.email)
        if auth_handler.verify_password(user_data.password, hash_password):
            token = auth_handler.encode_token(user_data.email)
            return {"message": "Login successful", "token": token}

        raise HTTPException(
            status_code=PASSWORD_DOESNT_MATCH, detail="Password does not match"
        )
    except UserNotFound as error:
        raise HTTPException(status_code=USER_NOT_FOUND, detail=str(error)) from error

    # Never reached
    # return {
    #    "message": "Login unsuccessful, something went wrong, but we don't know what it is"
    # }


@app.post("/login_admin/", status_code=200)
def login_admin(user_data: UserLogIn):
    """
    This function is the endpoint for the web backoffice front to log in an already existing admin

    :param user: The user to login.
    :return: Status code with a JSON message.
    """
    try:
        user = get_user_service(user_data.email)
        if not user.admin:
            raise HTTPException(
                status_code=USER_NOT_ADMIN, detail="User is not an admin"
            )
        if auth_handler.verify_password(user_data.password, user.password):
            token = auth_handler.encode_token(user_data.email)
            return {"message": "Login successful", "token": token}

        raise HTTPException(
            status_code=PASSWORD_DOESNT_MATCH, detail="Password does not match"
        )
    except UserNotFound as error:
        raise HTTPException(status_code=USER_NOT_FOUND, detail=str(error)) from error


class FollowUsernames(BaseModel):
    """
    This class is a Pydantic model for the request body.
    """

    username_follower: str
    username_following: str


@app.post("/follow")
def create_follow(follow_usernames: FollowUsernames):
    """
    This function creates a following relation between the given users.

    :param username_follower: Email of the user that will follow.
    :param username_following: Email of the user that is going to be followed.
    :return: Status code with a JSON message.
    """
    try:
        create_follow_service(
            follow_usernames.username_follower, follow_usernames.username_following
        )
    except UserNotFound as error:
        raise HTTPException(status_code=USER_NOT_FOUND, detail=str(error)) from error
    except UserCantFollowItself as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except FollowingRelationAlreadyExists as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return {"message": "Follow successful"}


@app.get("/follow/{username}")
def get_followers(username: str):
    """
    This function returns the users a username is followed by.

    :param username: Username of the user to get the followers of.
    :return: Status code with a JSON message.
    """
    try:
        user_list = get_all_followers(username)
        return generate_response_list(user_list)
    except UserNotFound as error:
        raise HTTPException(status_code=USER_NOT_FOUND, detail=str(error)) from error


@app.get("/following/{username}")
def get_following(username: str):
    """
    This function returns the users a username is following.

    :param username: Username of the user to get the following of.
    :return: Status code with a JSON message.
    """
    try:
        user_list = get_all_following(username)
        return generate_response_list(user_list)
    except UserNotFound as error:
        raise HTTPException(status_code=USER_NOT_FOUND, detail=str(error)) from error


@app.get("/follow/{username}/count")
def get_followers_count(username: str):
    """
    This function returns the number of followers of a username.

    :param username: Username of the user to get the followers count of.
    :return: Status code with a JSON message.
    """
    try:
        return get_followers_count_service(username)
    except UserNotFound as error:
        raise HTTPException(status_code=USER_NOT_FOUND, detail=str(error)) from error


@app.get("/following/{username}/count")
def get_following_count(username: str):
    """
    This function returns the number of users a username is following.

    :param username: Username of the user to get the following count of.
    :return: Status code with a JSON message.
    """
    try:
        return get_following_count_service(username)
    except UserNotFound as error:
        raise HTTPException(status_code=USER_NOT_FOUND, detail=str(error)) from error


@app.delete("/unfollow")
def unfollow(unfollow_usernames: FollowUsernames):
    """
    This function deletes a following relation between the given users.

    :param username_follower: Username of the user that will unfollow.
    :param username_following: Username of the user that is going to be unfollowed.
    :return: Status code with a JSON message.
    """
    try:
        return remove_follow_service(
            unfollow_usernames.username_follower, unfollow_usernames.username_following
        )
    except UserNotFound as error:
        raise HTTPException(status_code=USER_NOT_FOUND, detail=str(error)) from error


@app.get("/protected")
def protected(useremail=Depends(auth_handler.auth_wrapper)):
    """
    Wrapper for protected routes.
    """
    return {"email": useremail}


# Route to get user details
@app.get("/users/email/{email}", response_model=UserResponse)
def get_user(email: str):
    """
    This function is a function that retrieves an user by mail.

    :param email: The email of the user to get.
    :return: User details or a 404 response.
    """
    try:
        user = get_user_service(email)
        user = generate_response(user)
    except UserNotFound as error:
        raise HTTPException(status_code=USER_NOT_FOUND, detail=str(error)) from error
    return user


# Route to get user by username
@app.get("/users/username/{username}")
def get_user_by_username(username: str):
    """
    This function retrieves an user by username.

    :param username: The username of the user to get.
    :return: User details or a 404 response.
    """
    try:
        user = get_user_username(username)
        user = generate_response(user)
    except UserNotFound as error:
        raise HTTPException(status_code=USER_NOT_FOUND, detail=str(error)) from error
    return user


# Route to update user information
@app.put("/users/{email}/password")
def change_password(email: str, new_password: str):
    """
    This function is for changing the user's password

    :param email: The email of the user to update.
    :param new_password: User's new password.
    :return: Status code with a JSON message.
    """
    try:
        change_password_service(email, new_password)
    except UserNotFound as error:
        raise HTTPException(status_code=USER_NOT_FOUND, detail=str(error)) from error
    return {"message": "User information updated"}


@app.put("/users/{email}/bio")
def change_bio(email: str, new_bio: str):
    """
    This function is for changing the user's bio

    :param email: The email of the user to update.
    :param new_bio: User's new bio.
    :return: Status code with a JSON message.
    """
    try:
        change_bio_service(email, new_bio)
    except UserNotFound as error:
        raise HTTPException(status_code=USER_NOT_FOUND, detail=str(error)) from error
    return {"message": "User information updated"}


@app.put("/users/{email}/avatar")
def change_avatar(email: str, new_avatar: str):
    """
    This function is for changing the user's avatar

    :param email: The email of the user to update.
    :param new_avatar: User's new avatar.
    :return: Status code with a JSON message.
    """
    try:
        change_avatar_service(email, new_avatar)
    except UserNotFound as error:
        raise HTTPException(status_code=USER_NOT_FOUND, detail=str(error)) from error
    return {"message": "User information updated"}


@app.put("/users/{email}/name")
def change_name(email: str, new_name: str):
    """
    This function is for changing the user's name

    :param email: The email of the user to update.
    :param new_name: User's new name.
    :return: Status code with a JSON message.
    """
    try:
        change_name_service(email, new_name)
    except UserNotFound as error:
        raise HTTPException(status_code=USER_NOT_FOUND, detail=str(error)) from error
    return {"message": "User information updated"}


@app.put("/users/{email}/date_of_birth")
def change_date_of_birth(email: str, new_date_of_birth: str):
    """
    This function is for changing the user's date_of_birth

    :param email: The email of the user to update.
    :param new_date_of_birth: User's new date_of_birth.
    :return: Status code with a JSON message.
    """
    try:
        change_date_of_birth_service(email, new_date_of_birth)
    except UserNotFound as error:
        raise HTTPException(status_code=USER_NOT_FOUND, detail=str(error)) from error
    return {"message": "User information updated"}


@app.put("/users/{email}/last_name")
def change_last_name(email: str, new_last_name: str):
    """
    This function is for changing the user's last_name

    :param email: The email of the user to update.
    :param new_last_name: User's new last_name.
    :return: Status code with a JSON message.
    """
    try:
        change_last_name_service(email, new_last_name)
    except UserNotFound as error:
        raise HTTPException(status_code=USER_NOT_FOUND, detail=str(error)) from error
    return {"message": "User information updated"}


# Route to making an admin
@app.put("/users/{email}/make_admin")
def make_admin(email: str):
    """
    This function is a test function that mocks updating user information.

    :param email: The email of the user to update.
    :return: Status code with a JSON message.
    """
    try:
        make_admin_service(email)
    except UserNotFound as error:
        raise HTTPException(status_code=USER_NOT_FOUND, detail=str(error)) from error
    return {"message": email + " is now an admin"}


# Route to removing admin status
@app.put("/users/{email}/remove_admin")
def remove_admin_status(email: str):
    """
    This function is a test function that mocks updating user information.

    :param email: The email of the user to update.
    :return: Status code with a JSON message.
    """
    try:
        remove_admin_service(email)
    except UserNotFound as error:
        raise HTTPException(status_code=USER_NOT_FOUND, detail=str(error)) from error
    return {"message": email + " is no longer an admin"}


@app.delete("/users/{email}")
def delete_user(email: str):
    """
    This function is a test function that mocks deleting a user.

    :param email: The email of the user to delete.
    :return: Status code with a JSON message.
    """
    try:
        remove_user_email(email)
    except UserNotFound as error:
        raise HTTPException(status_code=USER_NOT_FOUND, detail=str(error)) from error
    return {"message": "User deleted"}


@app.get("/users/")
def get_all_users():
    """
    This function is an auxiliary function that returns all the users in the db

    :return: JSON of all users.
    """
    user_list = get_all_users_service()
    return generate_response_list(user_list)


@app.get("/following")
def get_all_following_relations():
    """
    This function is an auxiliary function that returns all the users in the db

    :return: JSON of all users.
    """
    return get_all_following_relations_service()


@app.get("/ping")
def ping():
    """
    This function is a test function that mocks a ping.

    :return: Status code with a JSON message.
    """
    return {"message": "pong"}


@app.get("/get_user_by_token", response_model=UserResponse)
def get_user_by_token(token: str = Header(...)):
    """
    This function retrieves an user by token.

    :param token: The authentication token.
    :return: User details or a 401 response.
    """
    try:
        user_email = auth_handler.decode_token(
            token
        )  # auth_handler.auth_wrapper(token)
        user = get_user_service(user_email)
        user = generate_response(user)
        return user
    except HTTPException as error:
        raise error
