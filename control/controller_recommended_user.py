"""
    Fast API Controller for Posts
"""
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

from repository.errors import ThisUserIsBlocked

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from control.common_setup import *

from control.utils.tracer import tracer
from control.utils.logger import logger

router = APIRouter()


@router.get(
    "/users/recommended",
    tags=["Recommended users"],
)
@tracer.start_as_current_span("Get recommended users")
def api_get_recommended_users(
    offset=Query(0, title="offset", description="offset for pagination"),
    amount=Query(10, title="ammount", description="max ammount of users to return"),
    user: callable = Depends(get_user_from_token),
):
    """
    This function returns the recommended users for a user.
    """
    try:
        recommended_users_db = get_recommended_accounts_for_a_user(
            int(user.get("id")), offset, amount
        )
        users = generate_response_recommended_users_from_db(recommended_users_db)
        logger.info(
            "User %s got recommended ussers with offset %s and amount %s successfully",
            user.get("email"),
            offset,
            amount,
        )
        return users
    except UserIsPrivate as error:
        logger.error(
            "User %s tried to get recommended ussers with offset"
            " %s and amount %s but user is private",
            user.get("email"),
            offset,
            amount,
        )
        raise HTTPException(status_code=403, detail=str(error)) from error
    except ThisUserIsBlocked as error:
        raise HTTPException(status_code=403, detail=str(error)) from error
    except Exception as error:
        logger.error(
            "User %s got an exception while trying to get recommended"
            " users with offset %s and amount %s but user is private: %s",
            user.get("email"),
            offset,
            amount,
            str(error),
        )
        raise HTTPException(status_code=500, detail=str(error)) from error
