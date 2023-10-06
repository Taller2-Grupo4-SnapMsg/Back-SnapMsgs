# pylint: disable=R0801
"""
    Fast API for the likes controller
"""
from fastapi import HTTPException, APIRouter, Header
import httpx

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.queries_like import *

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from control.common_setup import *

router = APIRouter()


def generate_like(like):
    """
    This function casts the orm_object into a pydantic model.
    (from data base object to json)
    """
    return LikeCreateRequest(user_id=like.user_id, post_id=like.post_id)


@router.post("/likes", tags=["Likes"])
async def api_create_like(post_id: int, token: str = Header(...)):
    """
    Creates a new like

    Args:
        like (Like): The like to create.

    Returns:
        Like: The like that was created.

    Raises:
        -
    """
    headers = {
        "Content-Type": "application/json;charset=utf-8",
        "accept": "application/json",
        "token": token,
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "https://loginback-lg51.onrender.com/user", headers=headers
            )
            print(f"RESPONSE: {response}")
            if response.status_code == 200:
                user = response.json()
                create_like(post_id, user.get("id"))
                return {"message": "Like created successfully"}
            raise HTTPException(status_code=400, detail={"Unknown error"})
        except httpx.HTTPError as error:
            raise HTTPException(status_code=400, detail={str(error)}) from error


@router.get("/likes/post/{post_id}", tags=["Likes"])
async def get_likes(post_id: int, token: str = Header(...)):
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
    headers = {
        "Content-Type": "application/json;charset=utf-8",
        "accept": "application/json",
        "token": token,
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "https://loginback-lg51.onrender.com/user", headers=headers
            )

            if response.status_code == 200:
                users = get_likes_from_post(post_id)
                return generate_response_users_with_user_from_back_user(users)

            raise HTTPException(status_code=400, detail={"Unknown error"})
        except PostNotFound as error:
            raise HTTPException(
                status_code=POST_NOT_FOUND, detail=str(error)
            ) from error
        except httpx.HTTPError as error:
            raise HTTPException(status_code=400, detail={str(error)}) from error


@router.get("/likes/post/{post_id}/count", tags=["Likes"])
async def get_number_of_likes(post_id: int, token: str = Header(...)):
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
    headers = {
        "Content-Type": "application/json;charset=utf-8",
        "accept": "application/json",
        "token": token,
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "https://loginback-lg51.onrender.com/user", headers=headers
            )

            if response.status_code == 200:
                likes = get_the_number_of_likes(post_id)
                return likes
        except httpx.HTTPError as error:
            raise HTTPException(status_code=400, detail={str(error)}) from error


@router.get("/likes/user/", tags=["Likes"])
async def get_likes_user(token: str = Header(...)):
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
    headers = {
        "Content-Type": "application/json;charset=utf-8",
        "accept": "application/json",
        "token": token,
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "https://loginback-lg51.onrender.com/user", headers=headers
            )

            if response.status_code == 200:
                user = response.json()
                posts = get_user_likes(user.get("id"))
                return generate_response_posts_with_user_from_back_user(posts, user)
            raise HTTPException(status_code=400, detail={"Unknown error"})
        except UserNotFound as error:
            raise HTTPException(
                status_code=USER_NOT_FOUND, detail=str(error)
            ) from error
        except httpx.HTTPError as error:
            raise HTTPException(status_code=400, detail={str(error)}) from error


@router.delete("/likes/user/post/{post_id}", tags=["Likes"])
async def api_delete_like(post_id: int, token: str = Header(...)):
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

    headers = {
        "Content-Type": "application/json;charset=utf-8",
        "accept": "application/json",
        "token": token,
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "https://loginback-lg51.onrender.com/user", headers=headers
            )

            if response.status_code == 200:
                user = response.json()
                delete_like(user.get("id"), post_id)
                return {"message": "Like delete successfully"}
        except LikeNotFound:
            return {"message": "The like dosen't exist"}
        except httpx.HTTPError as error:
            raise HTTPException(status_code=400, detail={str(error)}) from error


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
