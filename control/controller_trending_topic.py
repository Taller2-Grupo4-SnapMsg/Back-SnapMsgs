"""
    Fast API Controller for Trending Topics
"""
from fastapi import HTTPException, Header, APIRouter, Query

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.queries_trending_topic import *
from repository.queries.queries_get import *
from repository.queries.queries_hashtags import *
from repository.queries.queries_global import *
from repository.errors import ThisUserIsBlocked
from control.common_setup import *

router = APIRouter()


@router.get(
    "/trending_topics",
    tags=["Trending topics"],
)
async def api_get_trending_topics(
    offset=Query(0, title="offset", description="offset for pagination"),
    amount=Query(10, title="ammount", description="max ammount of users to return"),
    days=Query(
        7, title="days", description="to take into account the posts of the last x days"
    ),
    token: str = Header(...),
):
    """
    Get trending topics
    """
    try:
        _ = await get_user_from_token(token)
        trending_topics_db = get_trending_topics_with_count(
            int(offset), int(amount), int(days)
        )
        trending_topics = generate_response_trending_topics_from_db(trending_topics_db)
        return trending_topics
    # pylint: disable=R0801
    # I disable the "Similar lines in 2 files"
    except ThisUserIsBlocked as error:
        raise HTTPException(status_code=403, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


@router.get(
    "/posts/trending_topic/{hashtag}",
    tags=["Trending topics"],
)
async def api_get_posts_on_a_trending_topic(
    hashtag: str,
    offset=Query(0, title="offset", description="offset for pagination"),
    amount=Query(10, title="ammount", description="max ammount of users to return"),
    token: str = Header(...),
):
    """
    Get posts on a trending topic
    """
    try:
        user = await get_user_from_token(token)
        posts_db = get_posts_on_a_trending_topic(
            int(user.get("id")), hashtag, offset, amount
        )
        posts = generate_response_posts_from_db(posts_db)
        return posts
    except ThisUserIsBlocked as error:
        raise HTTPException(status_code=403, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error
