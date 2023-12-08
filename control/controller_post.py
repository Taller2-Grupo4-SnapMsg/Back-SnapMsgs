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
from repository.errors import ThisUserIsBlocked, OtherUserIsBlocked

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.errors import *

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from control.utils.tracer import tracer
from control.utils.logger import logger
from control.common_setup import *


router = APIRouter()

# ------------ POST  ------------


@router.post("/posts", tags=["Posts"])
@tracer.start_as_current_span("Create a post")
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
        logger.info("User %s created post %s successfully", user.get("email"), post_id)
        return {"message": "Post created successfully", "post_id": post_id}
    except EmptyPostError as error:
        logger.error(
            "User %s tried to create post but post was empty", user.get("email")
        )
        raise HTTPException(status_code=400, detail=str(error)) from error
    except TextTooLongError as error:
        logger.error(
            "User %s tried to create post but text too long", user.get("email")
        )
        raise HTTPException(status_code=400, detail=str(error)) from error
    except ThisUserIsBlocked as error:
        raise HTTPException(status_code=403, detail=str(error)) from error
    except Exception as error:
        logger.error(
            "User %s got an exception while trying to create a post: %s",
            user.get("email"),
            str(error),
        )
        raise HTTPException(status_code=500, detail=str(error)) from error


# # ------------- GET ----------------
# pylint: disable=C0103, W0622
@router.get(
    "/posts/profile/{user_visited_email}/oldest_date/{oldest_date_str}"
    "/amount/{amount}/only_reposts/",
    tags=["Posts"],
)
@tracer.start_as_current_span("Get posts and reposts from user visited")
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
        logger.info(
            "User %s got %s posts (only reposts? %s) from %s since %s successfully",
            user.get("email"),
            amount,
            only_reposts,
            user_visited_email,
            oldest_date_str,
        )

        return posts

    except UserIsPrivate as error:
        logger.error(
            "User %s tried to get posts and/or reposts from %s sice %s but %s is private",
            user.get("email"),
            user_visited_email,
            oldest_date_str,
            user_visited_email,
        )
        raise HTTPException(status_code=403, detail=str(error)) from error
    except ThisUserIsBlocked as error:
        raise HTTPException(status_code=403, detail=str(error)) from error
    except OtherUserIsBlocked as error:
        raise HTTPException(status_code=405, detail=str(error)) from error
    except UserDoesntHavePosts as error:
        logger.error(
            "User %s tried to get posts and/or reposts from %s sice %s but %s doesnt have posts",
            user.get("email"),
            user_visited_email,
            oldest_date_str,
            user_visited_email,
        )
        raise HTTPException(status_code=404, detail=str(error)) from error
    except Exception as error:
        logger.error(
            "User %s got an exception while trying to get posts from %s since % a post: %s",
            user.get("email"),
            user_visited_email,
            oldest_date_str,
            str(error),
        )
        raise HTTPException(status_code=500, detail=str(error)) from error


# pylint: disable=C0103, W0622
@router.get(
    "/posts/{post_id}",
    tags=["Posts"],
)
@tracer.start_as_current_span("Get post by id")
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
        logger.info(
            "User %s got post with id %s successfully", user.get("email"), post_id
        )
        return post
    except ThisUserIsBlocked as error:
        logger.error(
            "User %s tried to get post with id %s but user %s is blocked",
            user.get("email"),
            post_id,
            user.get("email"),
        )
        raise HTTPException(status_code=403, detail=str(error)) from error
    except PostNotFound as error:
        logger.error(
            "User %s tried to get post with id %s but post not found",
            user.get("email"),
            post_id,
        )
        raise HTTPException(status_code=404, detail=str(error)) from error
    except Exception as error:
        logger.error(
            "User %s got an exception while trying to get post with id %s: %s",
            user.get("email"),
            post_id,
            str(error),
        )
        raise HTTPException(status_code=500, detail=str(error)) from error


@router.get(
    "/posts/profile/{user_visited_email}",
    tags=["Posts"],
)
@tracer.start_as_current_span("Get posts from user visited")
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
        logger.info(
            "User %s got posts and reposts from %s successfully",
            user.get("email"),
            user_visited_email,
        )
        return get_amount_posts_from_users(int(user.get("id")), user_visited)

    except UserIsPrivate as error:
        logger.error(
            "User %s tried getting posts from %s, but %s is private",
            user.get("email"),
            user_visited_email,
            user_visited_email,
        )
        raise HTTPException(status_code=403, detail=str(error)) from error
    except ThisUserIsBlocked as error:
        raise HTTPException(status_code=403, detail=str(error)) from error
    except OtherUserIsBlocked as error:
        raise HTTPException(status_code=405, detail=str(error)) from error
    except UserDoesntHavePosts as error:
        logger.error(
            "User %s tried getting posts from %s, but %s doesnt have posts",
            user.get("email"),
            user_visited_email,
            user_visited_email,
        )
        raise HTTPException(status_code=404, detail=str(error)) from error
    except Exception as error:
        logger.error(
            "User %s got an exception while trying to get posts and reposts from %s: %s",
            user.get("email"),
            user_visited_email,
            str(error),
        )
        raise HTTPException(status_code=500, detail=str(error)) from error


@router.get(
    "/posts/feed/oldest_date/{oldest_date_str}/amount/{amount}",
    tags=["Posts"],
)
@tracer.start_as_current_span("Get Feed")
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
        logger.info(
            "User %s got its own feed with %s posts since %s successfully",
            user.get("email"),
            amount,
            oldest_date_str,
        )
        return posts
    except UserIsPrivate as error:
        logger.error(
            "User %s tried to get its own feed with %s posts since %s but user %s is private",
            user.get("email"),
            amount,
            oldest_date_str,
            user.get("email"),
        )
        raise HTTPException(status_code=403, detail=str(error)) from error
    except ThisUserIsBlocked as error:
        logger.error(
            "User %s tried to get its own feed with %s posts since %s but user %s is blocked",
            user.get("email"),
            amount,
            oldest_date_str,
            user.get("email"),
        )
        raise HTTPException(status_code=403, detail=str(error)) from error
    except UserDoesntHavePosts as error:
        logger.error(
            "User %s tried to get its own feed with %s posts since"
            " %s but user %s doesnt have any posts",
            user.get("email"),
            amount,
            oldest_date_str,
            user.get("email"),
        )
        raise HTTPException(status_code=404, detail=str(error)) from error
    except Exception as error:
        logger.error(
            "User %s got an exception while trying to get its own feed: %s",
            user.get("email"),
            str(error),
        )
        raise HTTPException(status_code=500, detail=str(error)) from error


@router.get(
    "/posts/statistics/from_date/{from_date_str}/to_date/{to_date_str}",
    tags=["Posts"],
)
@tracer.start_as_current_span("Get statistics")
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
        logger.info(
            "User %s got their statistics from %s to %s successfully",
            user.get("email"),
            from_date_str,
            to_date_str,
        )

        return statistics
    except ThisUserIsBlocked as error:
        raise HTTPException(status_code=403, detail=str(error)) from error
    except UserDoesntHavePosts as error:
        logger.info(
            "User %s tried to get their statistics from %s to %s but user doesnt have posts",
            user.get("email"),
            from_date_str,
            to_date_str,
        )
        raise HTTPException(status_code=404, detail=str(error)) from error
    except Exception as error:
        logger.error(
            "User %s got an exception while trying to get their statistics from %s to %s: %s",
            user.get("email"),
            from_date_str,
            to_date_str,
            str(error),
        )
        raise HTTPException(status_code=500, detail=str(error)) from error


@router.get(
    "/posts/search/hashtags/{hashtags}",
    tags=["Posts"],
)
@tracer.start_as_current_span("Get posts by hashtags")
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
        logger.info(
            "User %s got posts by hashtags %s with offset"
            " %s and amount %s successfully",
            user.get("email"),
            hashtags,
            offset,
            amount,
        )
        return posts
    except ThisUserIsBlocked as error:
        raise HTTPException(status_code=403, detail=str(error)) from error
    except UserIsPrivate as error:
        logger.info(
            "User %s tried to get posts by hashtags %s with offset"
            " %s and amount %s but user is private",
            user.get("email"),
            hashtags,
            offset,
            amount,
        )
        raise HTTPException(status_code=403, detail=str(error)) from error
    except UserDoesntHavePosts as error:
        logger.info(
            "User %s tried to get posts by hashtags %s with offset"
            " %s and amount %s but user doesnt have posts",
            user.get("email"),
            hashtags,
            offset,
            amount,
        )
        raise HTTPException(status_code=404, detail=str(error)) from error
    except Exception as error:
        logger.info(
            "User %s got an exception while trying to get posts"
            " by hashtags %s with offset %s and amount %s: %s",
            user.get("email"),
            hashtags,
            offset,
            amount,
            str(error),
        )
        raise HTTPException(status_code=500, detail=str(error)) from error


@router.get(
    "/posts/search/text/{text}",
    tags=["Posts"],
)
@tracer.start_as_current_span("Get posts by text")
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

        logger.info(
            "User %s got posts by text %s with offset %s and"
            " amount %s successfully",
            user.get("email"),
            text,
            offset,
            amount,
        )
        return posts
    except ThisUserIsBlocked as error:
        raise HTTPException(status_code=403, detail=str(error)) from error
    except UserIsPrivate as error:
        logger.info(
            "User %s tried to get posts by text %s with offset %s"
            " and amount %s but user is private",
            user.get("email"),
            text,
            offset,
            amount,
        )
        raise HTTPException(status_code=403, detail=str(error)) from error
    except UserDoesntHavePosts as error:
        logger.info(
            "User %s tried to get posts by text %s with offset %s"
            " and amount %s but user doesnt have posts",
            user.get("email"),
            text,
            offset,
            amount,
        )
        raise HTTPException(status_code=404, detail=str(error)) from error
    except Exception as error:
        logger.info(
            "User %s got an exception while trying to get posts by"
            " text %s with offset %s and amount %s: %s",
            user.get("email"),
            text,
            offset,
            amount,
            str(error),
        )
        raise HTTPException(status_code=500, detail=str(error)) from error


## ------- PUT ---------


@router.put("/posts/{post_id}", tags=["Posts"])
@tracer.start_as_current_span("Update post")
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
        logger.info(
            "User %s updated post with id %s successfully", user.get("email"), post_id
        )
        return {"message": "Post updated successfully"}
    except ThisUserIsBlocked as error:
        raise HTTPException(status_code=403, detail=str(error)) from error
    except UserIsPrivate as error:
        logger.error(
            "User %s tried to update post with id %s but user is private",
            user.get("email"),
            post_id,
        )
        raise HTTPException(status_code=403, detail=str(error)) from error
    except UserDoesntHavePosts as error:
        logger.error(
            "User %s tried to update post with id %s but user doesnt have posts",
            user.get("email"),
            post_id,
        )
        raise HTTPException(status_code=404, detail=str(error)) from error
    except Exception as error:
        logger.info(
            "User %s got an exception while trying to update post with id %s: %s",
            user.get("email"),
            post_id,
            str(error),
        )
        raise HTTPException(status_code=500, detail=str(error)) from error


## ------- DELETE ---------


@router.delete("/posts/{post_id}", tags=["Posts"])
@tracer.start_as_current_span("Delete post")
def api_delete_post(
    post_id: int,
    user: callable = Depends(get_user_from_token),
):
    """
    Deletes the post with the id
    """
    try:
        delete_post(post_id, user.get("id"))
        logger.info(
            "User %s deleted post with id %s successfully", user.get("email"), post_id
        )
        return {"message": "Post deleted successfully"}
    except ThisUserIsBlocked as error:
        raise HTTPException(status_code=403, detail=str(error)) from error
    except UserWithouPermission as error:
        logger.error(
            "User %s tried to delete post with id %s but user doesnt have permission",
            user.get("email"),
            post_id,
        )
        raise HTTPException(status_code=403, detail=str(error)) from error
    except UserDoesntHavePosts as error:
        logger.error(
            "User %s tried to delete post with id %s but user doesnt have posts",
            user.get("email"),
            post_id,
        )
        raise HTTPException(status_code=404, detail=str(error)) from error
    except Exception as error:
        logger.info(
            "User %s got an exception while trying to delete post with id %s: %s",
            user.get("email"),
            post_id,
            str(error),
        )
        raise HTTPException(status_code=500, detail=str(error)) from error
