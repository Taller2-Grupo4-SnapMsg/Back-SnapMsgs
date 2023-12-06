"""
    Fast API Controller for Trending Topics
"""
from fastapi import HTTPException, APIRouter, Query, Depends

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.queries_trending_topic import *
from repository.queries.queries_get import *
from repository.queries.queries_hashtags import *
from repository.queries.queries_global import *
from control.common_setup import *

from control.utils.tracer import tracer

router = APIRouter()


@router.get(
    "/trending_topics",
    tags=["Trending topics"],
)
@tracer.start_as_current_span("Get trending topics")
def api_get_trending_topics(
    offset=Query(0, title="offset", description="offset for pagination"),
    amount=Query(10, title="ammount", description="max ammount of users to return"),
    days=Query(
        7, title="days", description="to take into account the posts of the last x days"
    ),
    _: callable = Depends(get_user_from_token),
):
    """
    Get trending topics
    """
    try:
        trending_topics_db = get_trending_topics_with_count(
            int(offset), int(amount), int(days)
        )
        trending_topics = generate_response_trending_topics_from_db(trending_topics_db)
        return trending_topics
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


@router.get(
    "/posts/trending_topic/{hashtag}",
    tags=["Trending topics"],
)
@tracer.start_as_current_span("Get posts on a trending topic")
def api_get_posts_on_a_trending_topic(
    hashtag: str,
    offset=Query(0, title="offset", description="offset for pagination"),
    amount=Query(10, title="ammount", description="max ammount of users to return"),
    user: callable = Depends(get_user_from_token),
):
    """
    Get posts on a trending topic
    """
    try:
        posts_db = get_posts_on_a_trending_topic(
            int(user.get("id")), hashtag, offset, amount
        )
        posts = generate_response_posts_from_db(posts_db)
        return posts
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error
