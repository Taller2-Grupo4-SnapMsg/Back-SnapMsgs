"""
    Fast API for the likes controller
"""
from fastapi import HTTPException, Header
import httpx

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.queries import *

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from control.common_setup import *

# from control.controller_like import app
from fastapi import APIRouter

router = APIRouter()


def generate_like(like):
    """
    This function casts the orm_object into a pydantic model.
    (from data base object to json)
    """
    return LikeCreateRequest(user_id=like.user_id, post_id=like.post_id)


@router.post("/likes", tags=["Likes"])
async def api_create_like(like: LikeCreateRequest):
    """
    Creates a new like

    Args:
        like (Like): The like to create.

    Returns:
        Like: The like that was created.

    Raises:
        -
    """
    # deberia chequear si existen
    create_like(like.post_id, like.user_id)
    return {"message": "Like created successfully"}


@router.get("/likes", tags=["Likes"])
def get_all_likes():
    """
    Retrieve all likes in the system.

    This function returns a list of all likes recorded in the system.

    Returns:
        List[Dict[str, int]]: A list of dictionaries, each containing
        'user_id' and 'post_id' representing a like.

    Raises:
        No exceptions raised.
    """
    all_likes = get_all_the_likes()
    likes_data = [
        {"user_id": like.user_id, "post_id": like.id_post} for like in all_likes
    ]
    return likes_data


@router.get("/likes/post/{post_id}", tags=["Likes"])
def get_the_number_of_likes(post_id: int):
    """
    Retrieve the user IDs of users who liked a specific post.

    Given a `post_id`, this function returns a list of user IDs
    representing users who liked the post.

    Args:
        post_id (int): The ID of the post to retrieve likes for.

    Returns:
        List[int]: A list of user IDs representing users who liked the post.

    Raises:
        HTTPException: If the specified post does not exist, an
        HTTPException with a 404 status code is raised.
    """
    try:
        likes_list = get_likes_for_a_post(post_id)
        user_ids = [like.user_id for like in likes_list]
        return user_ids
    except PostNotFound as error:
        raise HTTPException(status_code=POST_NOT_FOUND, detail=str(error)) from error


@router.get("/likes/post/{post_id}/count", tags=["Likes"])
def get_number_of_likes(post_id: int):
    """
    Get the number of likes for a specific post.

    Args:
        post_id (int): The ID of the post for which you want to get
        the like count.

    Returns:
        int: The number of likes for the specified post.

    Raises:
        HTTPException: If the post with the specified ID is not found,
        it will raise an HTTP 404 error.
    """
    try:
        likes = get_likes_count(post_id)
        return likes
    except PostNotFound as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.get("/likes/user/{user_id}", tags=["Likes"])
def get_likes_user(user_id: int):
    """
    Retrieve the post IDs that a specific user has liked.

    Given a `user_id`, this function returns a list of post IDs representing
    the posts that the user has liked.

    Args:
        user_id (int): The ID of the user to retrieve liked posts for.

    Returns:
        List[int]: A list of post IDs representing posts liked by the user.

    Raises:
        HTTPException: If the specified user does not exist, an HTTPException
        with a 404 status code is raised.
    """
    try:
        liked_posts = get_all_the_likes_of_a_user(user_id)
        post_ids = [like.id_post for like in liked_posts]
        return post_ids
    except UserNotFound as error:
        raise HTTPException(status_code=USER_NOT_FOUND, detail=str(error)) from error


@router.delete("/likes/user/{user_id}/post/{post_id}", tags=["Likes"])
async def api_delete_like(user_id: int, post_id: int):
    """
    Deletes a like by user_id and post_id.

    Args:
        like_id (int): The ID of the like to be deleted.

    Returns:
        dict: A message indicating the successful deletion of the like.

    Raises:
        HTTPException: If the specified like does not exist, an
        HTTPException with a 404 status code is raised.
    """
    try:
        delete_like(user_id, post_id)
        return {"message": "Like deleted successfully"}
    except KeyError as error:
        raise HTTPException(
            status_code=LIKE_NOT_FOUND, detail="Like doesn't exist"
        ) from error
