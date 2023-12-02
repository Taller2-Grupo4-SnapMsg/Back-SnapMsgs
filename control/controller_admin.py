# controller_admin.py
"""
Router dedicated to the admin endpoints
"""
from fastapi import APIRouter, Header, Query
from fastapi.exceptions import HTTPException

from control.utils.tracer import tracer
from control.common_setup import (
    token_is_admin,
    BAD_REQUEST,
    MAX_AMMOUNT,
    generate_response_posts_from_db,
    generate_response_posts_from_db_for_admin,
)
from repository.errors import (
    UserNotFound,
    UserDoesntHavePosts,
)
from repository.queries.queries_get import (
    get_user_id_from_email,
)
from repository.queries.queries_admin import (
    get_posts_and_reposts_for_admin,
    get_posts_and_reposts_for_admin_user_id,
    get_posts_by_text_admin,
)

router = APIRouter()


@router.get("/admin/health", tags=["Admin"])
@tracer.start_as_current_span("Health Check")
def get_service_health_and_description():
    """
    Returns the health of the service
    """
    description = "SnapMsg's microservice handles everything"
    description += " related to the posts and their interactions"
    return {
        "status": "ok",
        "description": description,
        "creation_date": "27-09-2023",
    }


@router.get("/posts/admin/all", tags=["Admin"])
@tracer.start_as_current_span("Get all posts - Admin")
async def api_get_posts_for_admin(
    start: int = Query(0, title="start", description="start for pagination"),
    ammount: int = Query(10, title="ammount", description="ammount of posts"),
    token: str = Header(...),
):
    """
    This endpoint is used for admins, and is used to retrieve posts in a paginated way.

    param: start: The starting point of the pagination
    param: offset: The offset of the pagination
    param: token: The token of the ADMIN.

    return: A list of posts with no filters
    """
    try:
        if ammount > MAX_AMMOUNT:
            raise HTTPException(status_code=400, detail="Max ammount is 25")
        if not await token_is_admin(token):
            raise HTTPException(status_code=403, detail="Invalid token")
        posts_db = get_posts_and_reposts_for_admin(start, ammount)
        return generate_response_posts_from_db_for_admin(posts_db)
    except UserDoesntHavePosts as error:
        raise HTTPException(status_code=BAD_REQUEST, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


@router.get("/posts/admin/user", tags=["Admin"])
@tracer.start_as_current_span("Get posts from user - Admin")
async def api_get_posts_for_admin_user_id(
    email: str,
    start: int = Query(0, title="start", description="start for pagination"),
    ammount: int = Query(10, title="ammount", description="ammount of posts"),
    token: str = Header(...),
):
    """
    This endpoint is used for admins, and is used to retrieve posts from
    an user in a paginated way.

    param: user_email: The email of the user to retrieve posts from
    param: start: The starting point of the pagination
    param: offset: The offset of the pagination
    param: token: The token of the admin.

    return: A list of posts
    """
    try:
        if ammount > MAX_AMMOUNT:
            raise HTTPException(status_code=400, detail="Max ammount is 25")
        if not await token_is_admin(token):
            raise HTTPException(status_code=403, detail="Invalid token")
        user_id = get_user_id_from_email(email)
        posts_db = get_posts_and_reposts_for_admin_user_id(user_id, start, ammount)
        return generate_response_posts_from_db(posts_db)
    except UserDoesntHavePosts as error:
        raise HTTPException(status_code=BAD_REQUEST, detail=str(error)) from error
    except UserNotFound as error:
        raise HTTPException(status_code=BAD_REQUEST, detail=str(error)) from error


@router.get("/posts/admin/search/{text}", tags=["Admin"])
@tracer.start_as_current_span("Get posts by text - Admin")
async def api_get_posts_for_admin_search(
    text: str,
    offset=Query(0, title="offset", description="offset for pagination"),
    amount=Query(10, title="ammount", description="max ammount of users to return"),
    token: str = Header(...),
):
    """
    Endpoint used by admins to search for posts by text

    param: text: The text to search for
    param: offset: The offset for pagination
    param: amount: The max amount of posts to return
    param: token: The token of the admin.
    return: posts that contain the text
    """
    if not await token_is_admin(token):
        raise HTTPException(status_code=403, detail="Invalid token")
    try:
        posts_db = get_posts_by_text_admin(text, offset, amount)
        return generate_response_posts_from_db(posts_db)
    except Exception as error:
        raise HTTPException(status_code=500, detail="Internal server error") from error
