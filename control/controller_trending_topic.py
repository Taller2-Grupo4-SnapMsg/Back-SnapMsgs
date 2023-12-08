"""
    Fast API Controller for Trending Topics
"""
from fastapi import HTTPException, APIRouter, Query, Depends

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.queries_trending_topic import *
from repository.queries.queries_get import *
from repository.queries.queries_hashtags import *
from repository.queries.queries_global import *
from repository.errors import ThisUserIsBlocked
from control.common_setup import *

from control.utils.tracer import tracer
from control.utils.logger import logger

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
        7, title="days", description="to take into account"
        " the posts of the last x days"
    ),
    user: callable = Depends(get_user_from_token),
):
    """
    Get trending topics
    """
    try:
        trending_topics_db = get_trending_topics_with_count(
            int(offset), int(amount), int(days)
        )
        trending_topics = generate_response_trending_topics_from_db(trending_topics_db)
        logger.info(
            "User %s got the trending topics with offset"
            " %s, amount %s and days %s successfully",
            user.get("email"),
            offset,
            amount,
            days,
        )
        return trending_topics
    # pylint: disable=R0801
    # I disable the "Similar lines in 2 files"
    except ThisUserIsBlocked as error:
        logger.error(
            "User %s tried to get the trending topics with"
            " offset %s, amount %s and days %s but user is blocked",
            user.get("email"),
            offset,
            amount,
            days,
        )
        raise HTTPException(status_code=403, detail=str(error)) from error
    except Exception as error:
        logger.error(
            "User %s got an exception while trying to get the"
            " trending topics with offset %s, amount %s and days %s: %s",
            user.get("email"),
            offset,
            amount,
            days,
            str(error),
        )
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
        logger.info(
            "User %s got the posts from the hashtag %s with "
            "offset %s and amount %s successfully",
            user.get("email"),
            hashtag,
            offset,
            amount,
        )
        return posts
    except ThisUserIsBlocked as error:
        logger.error(
            "User %s tried to get posts from the hashtag %s with"
            " offset %s and amount %s but user is blocked",
            user.get("email"),
            hashtag,
            offset,
            amount,
        )
        raise HTTPException(status_code=403, detail=str(error)) from error
    except Exception as error:
        logger.error(
            "User %s got an exception while trying to get posts"
            " from the hashtag %s with offset %s and amount %s: %s",
            user.get("email"),
            hashtag,
            offset,
            amount,
            str(error),
        )
        raise HTTPException(status_code=500, detail=str(error)) from error
