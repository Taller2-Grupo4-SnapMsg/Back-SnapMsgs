"""
    Fast API
"""
from fastapi import HTTPException, Header, APIRouter
import httpx
from datetime import datetime

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.queries_post import *

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.queries_hashtag import *

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.queries_global import *

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from control.common_setup import *

router = APIRouter()

# ------------ POST  ------------


@router.post("/posts", tags=["Posts"])
async def api_create_post(post: PostCreateRequest, token: str = Header(...)):
    try:
        user = await get_user_from_token(token)
        post = create_post(int(user.get("id")), post.content, post.image, post.hashtags)
        if post is None:
            raise HTTPException(status_code=500, detail="Error while creating post")
        # create_hashtags(created_post.id, post.hashtags)  # Convierte el conjunto a lista
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al crear etiquetas")

    return {"message": "Post created successfully"}


# # ------------- GET ----------------


# pylint: disable=C0103, W0622
@router.get("/posts/profile/{date_str}/amount/{n}", tags=["Posts"])  # ANDA
async def api_get_posts_user_by_token(n: int, date_str: str, token: str = Header(...)):
    """
    Gets all posts from a user by token

    Returns: All posts made by that user
    """
    date = datetime.strptime(date_str, "%Y-%m-%d_%H:%M:%S")
    user = await get_user_from_token(token)
    posts_db = get_post_from_user_b_to_user_a(
        int(user.get("id")), int(user.get("id")), n, date
    )
    posts = generate_response_posts_from_db(posts_db)
    return posts


# pylint: disable=C0103, W0622
@router.get("/posts/profile/{user_id}/{date_str}/amount/{n}", tags=["Posts"])
async def api_get_posts_by_user_id(
    user_id: int, n: int, date_str: str, token: str = Header(...)
):
    """
    Gets all posts from a user by id

    Returns: All posts made by that user
    """
    date = datetime.strptime(date_str, "%Y-%m-%d_%H:%M:%S")
    user = await get_user_from_token(token)
    posts_db = get_post_from_user_b_to_user_a(int(user.get("id")), user_id, n, date)
    posts = generate_response_posts_from_db(posts_db)
    return posts


# pylint: disable=C0103, W0622
@router.get("/posts/feed/{date_str}/amount/{n}", tags=["Posts"])
async def api_get_posts_user_feed(n: int, date_str: str, token: str = Header(...)):
    """
    Gets all posts from a user by id
    """
    date = datetime.strptime(date_str, "%Y-%m-%d_%H:%M:%S")
    user = await get_user_from_token(token)
    posts_db = get_post_for_user_feed(int(user.get("id")), n, date)
    posts = generate_response_posts_from_db(posts_db)
    return posts


# pylint: disable=C0103, W0622
@router.get("/posts/feed/followings/{date_str}/amount/{n}", tags=["Posts"])
async def api_get_posts_users_that_I_follow(
    n: int, date_str: str, token: str = Header(...)
):
    """
    Gets all posts from a user by id

    Returns: All posts made by that user
    """
    date = datetime.strptime(date_str, "%Y-%m-%d_%H:%M:%S")
    user = await get_user_from_token(token)
    posts_db = get_posts_from_users_followed_by_user(int(user.get("id")), n, date)
    posts = generate_response_posts_from_db(posts_db)
    return posts


# pylint: disable=C0103, W0622
@router.get("/posts/feed/interest/{date_str}/amount/{n}", tags=["Posts"])
async def api_get_posts_users_interest(n: int, date_str: str, token: str = Header(...)):
    """
    Gets all posts from a user by id

    Returns: All posts made by that user
    """
    date = datetime.strptime(date_str, "%Y-%m-%d_%H:%M:%S")
    user = await get_user_from_token(token)
    posts_db = get_public_posts_user_is_interested_in(int(user.get("id")), n, date)
    posts = generate_response_posts_from_db(posts_db)
    return posts


@router.get("/posts/{id}", tags=["Posts"])
async def api_get_post_by_id(id: int, token: str = Header(...)):
    """
    Gets the post with the id

    Args: Id of the post
    Returns: The post with that Id
    Raises: HTTPEXCEPTION with code 404 if post not found
    """
    user = await get_user_from_token(token)
    post_db = get_post_by_id_global(int(user.get("id")), id)
    (
        post_info,
        user,
        user_repost,
        likes_count,
        reposts_count,
        hashtags,
        is_repost,
    ) = post_db
    if likes_count is None:
        likes_count = 0
    if reposts_count is None:
        reposts_count = 0
    post = generate_post_from_db(
        post_info, user, likes_count, reposts_count, hashtags, user_repost, is_repost
    )
    return post


## ------- PUT ---------


@router.put("/posts/{post_id}", tags=["Posts"])
async def api_update_post(
    post_id: int, post_data: PostCreateRequest, token: str = Header(...)
):
    """
    Update the post with the id
    """
    user = await get_user_from_token(token)
    delete_hashtags_for_post(post_id)
    post = update_post(post_id, user.get("id"), post_data.content, post_data.image)
    create_hashtags(post.id, post_data.hashtags)
    return {"message": "Post updated successfully"}


## ------- DELETE ---------


@router.delete("/posts/{id}/", tags=["Posts"])
async def api_delete_post(id: int, token: str = Header(...)):
    """
    Deletes the post with the id
    """
    _ = await get_user_from_token(token)
    delete_post(id)
    return {"message": "Post deleted successfully"}
