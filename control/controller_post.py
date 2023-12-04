"""
    Fast API Controller for Posts
"""
from datetime import datetime
from fastapi import HTTPException, APIRouter, Query, Depends

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.queries_posts import *

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.queries_get import *

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.queries_admin import *

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.queries_hashtags import *

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.queries_global import *

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.errors import *

# pylint: disable=C0114, W0401, W0614, E0602, E0401
# from control.utils.tracer import tracer
from control.common_setup import *

router = APIRouter()

# ------------ POST  ------------


@router.post("/posts", tags=["Posts"])
# @tracer.start_as_current_span("Create a post")
def api_create_post(
    post: PostCreateRequest,
    user: callable = Depends(get_user_from_token),
):
    """
    Create a post with its image uploaded to Fire`base and hashtags created accordingly.
    Returns post or raises an exception with error code 500.
    """
    try:
        # pylint: disable=E1121, R0913
        validate_that_there_is_at_least_text_or_image(post.content, post.image)
        valid_content(post.content)
        post_id = create_post(
            int(user.get("id")), post.content, post.image, post.hashtags, post.mentions
        )
        return {"message": "Post created successfully", "post_id": post_id}
    except EmptyPostError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except TextTooLongError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


# # ------------- GET ----------------
# pylint: disable=C0103, W0622
@router.get(
    "/posts/profile/{user_visited_email}/oldest_date/{oldest_date_str}"
    "/amount/{amount}/only_reposts/",
    tags=["Posts"],
)
# @tracer.start_as_current_span("Get posts and reposts from user visited")
def api_get_posts_and_reposts_from_user_visited(
    user_visited_email: str,
    oldest_date_str: str,
    amount: int,
    only_reposts: bool = Query(...),
    user: callable = Depends(get_user_from_token),
):
    """
    Gets all posts and reposts from user visited as user visitor

    Returns: All posts and reposts made by that user
    """
    try:
        oldest_date = datetime.datetime.strptime(oldest_date_str, "%Y-%m-%d_%H:%M:%S")
        user_visited = get_user_id_from_email(user_visited_email)
        posts_db = get_posts_and_reposts_from_users(
            int(user.get("id")), user_visited, oldest_date, amount, only_reposts
        )

        posts = generate_response_posts_from_db(posts_db)

        return posts

    except UserIsPrivate as error:
        raise HTTPException(status_code=403, detail=str(error)) from error
    except UserDoesntHavePosts as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


# pylint: disable=C0103, W0622
@router.get(
    "/posts/{post_id}",
    tags=["Posts"],
)
# @tracer.start_as_current_span("Get post by id")
def api_get_post_by_id(
    post_id: int,
    user: callable = Depends(get_user_from_token),
):
    """
    Get post by id
    """
    try:
        post_db = get_post_by_id(int(user.get("id")), post_id)
        post = generate_response_posts_from_db(post_db)
        return post
    except PostNotFound as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


@router.get(
    "/posts/profile/{user_visited_email}",
    tags=["Posts"],
)
# @tracer.start_as_current_span("Get posts from user visited")
def api_get_amount_posts_from_user_visited(
    user_visited_email: str,
    user: callable = Depends(get_user_from_token),
):
    """
    Gets all posts and reposts from user visited as user visitor

    Returns: All posts and reposts made by that user
    """
    try:
        user_visited = get_user_id_from_email(user_visited_email)
        return get_amount_posts_from_users(int(user.get("id")), user_visited)

    except UserIsPrivate as error:
        raise HTTPException(status_code=403, detail=str(error)) from error
    except UserDoesntHavePosts as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


@router.get(
    "/posts/feed/oldest_date/{oldest_date_str}/amount/{amount}",
    tags=["Posts"],
)
# @tracer.start_as_current_span("Get Feed")
def api_get_feed(
    oldest_date_str: str,
    amount: int,
    user: callable = Depends(get_user_from_token),
):
    """
    Gets all posts from user visited as user visitor

    Returns: All posts and reposts made by that user
    """
    try:
        oldest_date = datetime.datetime.strptime(oldest_date_str, "%Y-%m-%d_%H:%M:%S")

        posts_db = get_posts_and_reposts_feed(int(user.get("id")), oldest_date, amount)
        posts = generate_response_posts_from_db(posts_db)

        return posts
    except UserIsPrivate as error:
        raise HTTPException(status_code=403, detail=str(error)) from error
    except UserDoesntHavePosts as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


@router.get(
    "/posts/statistics/from_date/{from_date_str}/to_date/{to_date_str}",
    tags=["Posts"],
)
# @tracer.start_as_current_span("Get statistics")
def api_get_statistics(
    from_date_str: str,
    to_date_str: str,
    user: callable = Depends(get_user_from_token),
):
    """
    Gets all posts from user visited as user visitor

    Returns: All posts and reposts made by that user
    """
    try:
        from_date = datetime.datetime.strptime(from_date_str, "%Y-%m-%d_%H:%M:%S")
        to_date = datetime.datetime.strptime(to_date_str, "%Y-%m-%d_%H:%M:%S")

        statistics = get_statistics(int(user.get("id")), from_date, to_date)

        return statistics
    except UserDoesntHavePosts as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


@router.get(
    "/posts/search/hashtags/{hashtags}",
    tags=["Posts"],
)
# @tracer.start_as_current_span("Get posts by hashtags")
def api_get_posts_by_hashtags(
    hashtags: str,
    offset=Query(0, title="offset", description="offset for pagination"),
    amount=Query(10, title="ammount", description="max ammount of users to return"),
    user: callable = Depends(get_user_from_token),
):
    """
    This fuction gets all posts that have the hashtags passed as parameter
    :param hashtags: The hashtags to search for
    :param offset: The offset for pagination
    :param amount: The max amount of posts to return
    :param token: The authentication token.
    :return: A list of posts
    """
    try:
        hashtag_list = hashtags.split(",")

        posts_db = get_posts_by_hashtags(
            int(user.get("id")), hashtag_list, offset, amount
        )
        posts = generate_response_posts_from_db(posts_db)

        return posts
    except UserIsPrivate as error:
        raise HTTPException(status_code=403, detail=str(error)) from error
    except UserDoesntHavePosts as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


@router.get(
    "/posts/search/text/{text}",
    tags=["Posts"],
)
# @tracer.start_as_current_span("Get posts by text")
def api_get_posts_by_text(
    text: str,
    offset=Query(0, title="offset", description="offset for pagination"),
    amount=Query(10, title="ammount", description="max ammount of users to return"),
    user: callable = Depends(get_user_from_token),
):
    """
    This fuction gets all posts that have the text passed as parameter on it's body.
    :param text: The text to search for
    :param offset: The offset for pagination
    :param amount: The max amount of posts to return
    :param token: The authentication token.
    :return: A list of posts
    """
    try:
        posts_db = get_posts_by_text(int(user.get("id")), text, offset, amount)
        posts = generate_response_posts_from_db(posts_db)

        return posts
    except UserIsPrivate as error:
        raise HTTPException(status_code=403, detail=str(error)) from error
    except UserDoesntHavePosts as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


## ------- PUT ---------


@router.put("/posts/{post_id}", tags=["Posts"])
# @tracer.start_as_current_span("Update post")
def api_update_post(
    post_id: int,
    post_data: PostCreateRequest,
    user: callable = Depends(get_user_from_token),
):
    """
    Update the post with the id
    """
    try:
        update_post(
            post_id,
            user.get("id"),
            post_data.content,
            post_data.image,
            post_data.hashtags,
            post_data.mentions,
        )
        return {"message": "Post updated successfully"}
    except UserIsPrivate as error:
        raise HTTPException(status_code=403, detail=str(error)) from error
    except UserDoesntHavePosts as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


## ------- DELETE ---------


@router.delete("/posts/{post_id}", tags=["Posts"])
# @tracer.start_as_current_span("Delete post")
def api_delete_post(
    post_id: int,
    user: callable = Depends(get_user_from_token),
):
    """
    Deletes the post with the id
    """
    try:
        delete_post(post_id, user.get("id"))
        return {"message": "Post deleted successfully"}
    except UserWithouPermission as error:
        raise HTTPException(status_code=403, detail=str(error)) from error
    except UserDoesntHavePosts as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error
