"""
    Fast API
"""
from fastapi import HTTPException, Header
import httpx

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.queries import *

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from control.common_setup import *
from fastapi import APIRouter

router = APIRouter()

# ------------ POST  ------------


@router.post("/posts", tags=["Posts"])
async def api_create_post(post: PostCreateRequest, token: str = Header(...)):
    """
    Creates a new post

    Args:
        post (Post): The post to create.

    Returns:
        Post: The post that was created.

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
            # Realiza una solicitud GET al endpoint de tu otro backend
            response = await client.get(
                "https://loginback-lg51.onrender.com/user", headers=headers
            )

            # Verifica si la solicitud se completó con éxito (código de respuesta 200)
            if response.status_code == 200:
                create_post(post.user_id, post.content, post.image)
                return {"message": "Post created successfully"}

            raise HTTPException(status_code=400, detail={"Unknown error"})
        except httpx.HTTPError as error:
            # Maneja las excepciones de HTTP, por ejemplo, si la solicitud falla
            raise HTTPException(status_code=400, detail={str(error)}) from error


# ------------- GET ----------------


@router.get("/posts", tags=["Posts"])
async def api_get_posts(token: str = Header(...)):
    """
    Gets all the posts ever created.
    Use with caution!

    Args:
        -

    Returns:
        List of Posts

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
            # Realiza una solicitud GET al endpoint de tu otro backend
            response = await client.get(
                "https://loginback-lg51.onrender.com/user", headers=headers
            )
            # Verifica si la solicitud se completó con éxito (código de respuesta 200)
            if response.status_code == 200:
                posts_and_users = get_posts()
                return generate_response_posts_with_users_from_db(posts_and_users)
            raise HTTPException(status_code=400, detail={"Unknown error"})
        except httpx.HTTPError as error:
            # Maneja las excepciones de HTTP, por ejemplo, si la solicitud falla
            raise HTTPException(status_code=400, detail={str(error)}) from error


# pylint: disable=C0103, W0622
@router.get("/posts/{id}", tags=["Posts"])
async def api_get_post_by_id(id: int, token: str = Header(...)):
    """
    Gets the post with the id passed
    Args:
        :param id: Id of the post

    Returns:
        The post with that Id

    Raises:
        HTTPEXCEPTION with code 404 if post not found
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
            # Verifica si la solicitud se completó con éxito (código de respuesta 200)
            if response.status_code == 200:
                user = response.json()
                # pylint: disable=C0103, W0622
                post = get_post_by_id(id)
                if post is None:
                    raise HTTPException(
                        status_code=POST_NOT_FOUND, detail="Post not found"
                    )
                return generate_post_from_back_user(post, user)

            raise HTTPException(status_code=400, detail={"Unknown error"})
        except httpx.HTTPError as error:
            # Maneja las excepciones de HTTP, por ejemplo, si la solicitud falla
            raise HTTPException(status_code=400, detail={str(error)}) from error


# pylint: disable=C0103, W0622
@router.get("/posts/user/", tags=["Posts"])  # ANDA
async def api_get_posts_by_user(token: str = Header(...)):
    """
    Gets all posts made by that user
    Use with caution!

    Returns:
        All posts made by that user

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
            print(token)
            response = await client.get(
                "https://loginback-lg51.onrender.com/user", headers=headers
            )
            # Verifica si la solicitud se completó con éxito (código de respuesta 200)
            if response.status_code == 200:
                user = response.json()
                posts = get_posts_by_user_id(int(user.get("id")))
                if posts is None:
                    raise HTTPException(
                        status_code=POST_NOT_FOUND, detail="Posts not found"
                    )
                return generate_response_posts_with_user_from_back_user(posts, user)
            raise HTTPException(status_code=400, detail={"Unknown error"})
        except httpx.HTTPError as error:
            # Maneja las excepciones de HTTP, por ejemplo, si la solicitud falla
            raise HTTPException(status_code=400, detail={str(error)}) from error


# # pylint: disable=W0511
# # TODO
# @router.get("/posts/user/{id}/date/{date}")
# async def api_get_posts_by_user_and_date(id: int, date: str):
#     """
#     Gets all posts made by that user that date

#     Args:
#         :param id: Id of the user
#         :param date: Specific date as a string with format "YYYY-MM-DD"

#     Returns:
#         All posts made by that user that date

#     Raises:
#         ValueError: if invalid date format
#     """
#     try:
#         # está comparando YYYY-MM-DD contra YYYY-MM-DD HH-MM-SS que hay en la bdd
#         datetime_date = strptime(date, "%Y-%m-%d")

#         post = get_posts_by_user_and_date(id, datetime_date)
#         return generate_response_posts(post)
#     except ValueError as error:
#         raise HTTPException(
#             status_code=BAD_REQUEST,
#             detail="Invalid\
#                             date format. Expected format: YYYY-MM-DD",
#         ) from error


@router.get("/posts/user/amount/{x}", tags=["Posts"])
async def api_get_x_newest_posts_by_user(x: int, token: str = Header(...)):
    """
    Gets x amount of newest posts made by that user (the owner of the token)

    Args:
        :param x: amount of posts to search

    Returns:
        All x posts made by that user. If user made less
        than x posts, all the posts will be returned.

    Raises:

    """
    headers = {
        "Content-Type": "application/json;charset=utf-8",
        "accept": "application/json",
        "token": token,
    }
    if x <= 0:
        raise HTTPException(
            status_code=BAD_REQUEST, detail="Amount must be greater than 0"
        )

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "https://loginback-lg51.onrender.com/user", headers=headers
            )
            # Verifica si la solicitud se completó con éxito (código de respuesta 200)
            if response.status_code == 200:
                user = response.json()
                posts = get_x_newest_posts_by_user(int(user.get("id")), x)
                return generate_response_posts_with_user_from_back_user(posts, user)
            raise HTTPException(status_code=400, detail={"Unknown error"})
        except httpx.HTTPError as error:
            # Maneja las excepciones de HTTP, por ejemplo, si la solicitud falla
            raise HTTPException(status_code=400, detail={str(error)}) from error


@router.get("/posts/amount/{x}", tags=["Posts"])
async def api_get_x_newest_posts(x: int, token: str = Header(...)):
    """
    Gets x amount of newest posts made in general

    Args:
        :param x: amount of posts to search

    Returns:
        All x posts made in general. If there are less
        than x posts created, all the posts will be returned.

    Raises:

    """
    headers = {
        "Content-Type": "application/json;charset=utf-8",
        "accept": "application/json",
        "token": token,
    }
    if x <= 0:
        raise HTTPException(
            status_code=BAD_REQUEST, detail="Amount must be greater than 0"
        )

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "https://loginback-lg51.onrender.com/user", headers=headers
            )
            # Verifica si la solicitud se completó con éxito (código de respuesta 200)
            if response.status_code == 200:
                posts = get_x_newest_posts(x)
                return generate_response_posts_with_users_from_db(posts)
            raise HTTPException(status_code=400, detail={"Unknown error"})
        except httpx.HTTPError as error:
            # Maneja las excepciones de HTTP, por ejemplo, si la solicitud falla
            raise HTTPException(status_code=400, detail={str(error)}) from error


# # ------- DELETE ---------


@router.delete("/post/{id}", tags=["Posts"])
async def api_delete_post(id: int, token: str = Header(...)):
    """
    Gets x amount of newest posts made in general

    Args:
        :param x: amount of posts to search

    Returns:
        All x posts made in general. If there are less than x posts
        created, all the posts will be returned.

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
            # Verifica si la solicitud se completó con éxito (código de respuesta 200)
            if response.status_code == 200:
                delete_post(id)
                return {"message": "Post deleted successfully"}
            raise HTTPException(status_code=400, detail={"Unknown error"})
        except KeyError as error:
            raise HTTPException(
                status_code=POST_NOT_FOUND, detail="Post doesnt exist"
            ) from error
        except httpx.HTTPError as error:
            # Maneja las excepciones de HTTP, por ejemplo, si la solicitud falla
            raise HTTPException(status_code=400, detail={str(error)}) from error
