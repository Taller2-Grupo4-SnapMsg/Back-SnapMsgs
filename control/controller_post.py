"""
    Fast API Controller for Posts
"""
from datetime import datetime
from fastapi import HTTPException, Header, APIRouter

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.queries_posts import *


# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.queries_get import *

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.queries_hashtags import *

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.queries_global import *

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from control.common_setup import *

router = APIRouter()

# ------------ POST  ------------


@router.post("/posts", tags=["Posts"])
async def api_create_post(post: PostCreateRequest, token: str = Header(...)):
    """
    Create a post with its image uploaded to Firebase and hashtags created accordingly.
    Returns post or raises an exception with error code 500.
    """
    try:
        user = await get_user_from_token(token)
        # pylint: disable=E1121, R0913
        create_post(int(user.get("id")), post.content, post.image, post.hashtags)
        return {"message": "Post created successfully"}
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


# # ------------- GET ----------------
# pylint: disable=C0103, W0622
@router.get(
    "/posts/profile/{user_visited_email}/oldest_date/{oldest_date_str}"
    "/amount/{amount}/only_reposts/{only_reposts}",
    tags=["Posts"],
)
async def api_get_posts_and_reposts_from_user_visited(
    user_visited_email: str,
    oldest_date_str: str,
    amount: int,
    only_reposts_str: str,
    token: str = Header(...),
):
    """
    Gets all posts and reposts from user visited as user visitor

    Returns: All posts and reposts made by that user
    """
    try:
        oldest_date = datetime.datetime.strptime(oldest_date_str, "%Y-%m-%d_%H:%M:%S")
        user_visited = get_user_id_from_email(user_visited_email)

        only_reposts = False
        if only_reposts_str in ("True", "true"):
            only_reposts = True

        user = await get_user_from_token(token)

        posts_db = get_posts_and_reposts_from_users(
            int(user.get("id")), user_visited, oldest_date, amount, only_reposts
        )
        posts = generate_response_posts_from_db(posts_db)

        return posts
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


@router.get(
    "/posts/feed/oldest_date/{oldest_date_str}/amount/{amount}",
    tags=["Posts"],
)
async def api_get_posts_and_reposts_based_on_interests(
    oldest_date_str: str, amount: int, token: str = Header(...)
):
    """
    Gets all posts from user visited as user visitor

    Returns: All posts and reposts made by that user
    """
    try:
        oldest_date = datetime.datetime.strptime(oldest_date_str, "%Y-%m-%d_%H:%M:%S")
        user = await get_user_from_token(token)

        posts_db = get_posts_and_reposts_feed(int(user.get("id")), oldest_date, amount)
        posts = generate_response_posts_from_db(posts_db)

        return posts
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


## ------- PUT ---------


@router.put("/posts/{post_id}", tags=["Posts"])
async def api_update_post(
    post_id: int, post_data: PostCreateRequest, token: str = Header(...)
):
    """
    Update the post with the id
    """
    try:
        user = await get_user_from_token(token)
        update_post(
            post_id,
            user.get("id"),
            post_data.content,
            post_data.image,
            post_data.hashtags,
        )
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error
    return {"message": "Post updated successfully"}


## ------- DELETE ---------


@router.delete("/posts/{post_id}/", tags=["Posts"])
async def api_delete_post(post_id: int, token: str = Header(...)):
    """
    Deletes the post with the id
    """
    try:
        user = await get_user_from_token(token)
        delete_post(post_id, user.get("id"))
        return {"message": "Post deleted successfully"}
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error
