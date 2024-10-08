# pylint: disable=R0801
"""
Fast API for the favorites controller
"""
from fastapi import APIRouter, Depends

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.queries_favorites import *
from repository.queries.queries_global import get_content_id_from_post
from repository.queries.queries_get import *

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from control.common_setup import *

from control.utils.tracer import tracer
from control.utils.logger import logger

router = APIRouter()


@router.post("/favorites/{post_id}", tags=["Favorites"])
@tracer.start_as_current_span("Add a favorite to a post")
def api_create_favorite(
    post_id: int,
    user: callable = Depends(get_user_from_token),
):
    """
    Creates a new favorite.
    """
    try:
        content_id = get_content_id_from_post(post_id)
        create_favorite(post_id, content_id, user.get("id"))
        logger.info("User %s created a favorite of post %s", user.get("email"), post_id)
        return {"message": "Favorite created successfully"}
    except PostNotFound as error:
        logger.error(
            "User %s tried to get post with id %s but post not found",
            user.get("email"),
            post_id,
        )
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ThisUserIsBlocked as error:
        raise HTTPException(status_code=403, detail=str(error)) from error
    except DatabaseError as db_error:
        logger.error(
            "User %s got Database error while trying to get post with id %s: %s",
            user.get("email"),
            post_id,
            str(db_error),
        )
        raise HTTPException(
            status_code=400, detail="Post doesnt exist or favorite already exists"
        ) from db_error
    except Exception as error:
        logger.error(
            "User %s got an exception while trying to get post with id %s: %s",
            user.get("email"),
            post_id,
            str(error),
        )
        raise HTTPException(status_code=500, detail=str(error)) from error


@router.delete("/favorites/{post_id}", tags=["Favorites"])
@tracer.start_as_current_span("Remove a favorite from a post")
def api_delete_favorite(
    post_id: int,
    user: callable = Depends(get_user_from_token),
):
    """
    Deletes a favorite given by the user to a specific post.
    """
    try:
        content_id = get_content_id_from_post(post_id)
        delete_favorite(content_id, user.get("id"))
        logger.info("User %s deleted a favorite of post %s", user.get("email"), post_id)
        return {"message": "Favorite deleted successfully"}
    except FavoriteNotFound as error:
        logger.error(
            "User %s tried to get post with id %s but favorite not found",
            user.get("email"),
            post_id,
        )
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ThisUserIsBlocked as error:
        raise HTTPException(status_code=403, detail=str(error)) from error
    except Exception as error:
        logger.error(
            "User %s got an exception while trying to get post with id %s: %s",
            user.get("email"),
            post_id,
            str(error),
        )
        raise HTTPException(status_code=500, detail=str(error)) from error


# pylint: disable=C0103, W0622
@router.get(
    "/favorites/profile/{user_visited_email}/oldest_date/{oldest_date_str}"
    "/amount/{amount}",
    tags=["Favorites"],
)
@tracer.start_as_current_span("Get all favorites from user visited")
def api_get_favorites_from_user_visited(
    user_visited_email: str,
    oldest_date_str: str,
    amount: int,
    user: callable = Depends(get_user_from_token),
):
    """
    Gets all favorites posts from user visited as user visitor
    """
    try:
        oldest_date = datetime.datetime.strptime(oldest_date_str, "%Y-%m-%d_%H:%M:%S")
        user_visited = get_user_id_from_email(user_visited_email)
        posts_db = get_favorites_from_user(
            int(user.get("id")), user_visited, oldest_date, amount
        )
        posts = generate_response_posts_from_db(posts_db)
        logger.info(
            "User %s got %s amount of favorite posts since %s from user %s",
            user.get("email"),
            amount,
            oldest_date,
            user_visited_email,
        )
        return posts
    except UserIsPrivate as error:
        logger.error(
            "User %s tried to get favorite posts from %s but %s is private",
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
            "User %s tried to get favorite posts from %s but %s has no posts",
            user.get("email"),
            user_visited_email,
            user_visited_email,
        )
        raise HTTPException(status_code=404, detail=str(error)) from error
    except Exception as error:
        logger.error(
            "User %s got an exception while trying to get %s favorite posts since %s from %s: %s",
            user.get("email"),
            amount,
            oldest_date_str,
            user_visited_email,
            str(error),
        )
        raise HTTPException(status_code=500, detail=str(error)) from error
