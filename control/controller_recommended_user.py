"""
    Fast API Controller for Posts
"""
from fastapi import HTTPException, Header, APIRouter, Query

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
from control.common_setup import *
from control.utils.tracer import tracer

router = APIRouter()


@router.get(
    "/users/recommended",
    tags=["Recommended users"],
)
@tracer.start_as_current_span("Get recommended users")
def api_get_recommended_users(
    offset=Query(0, title="offset", description="offset for pagination"),
    amount=Query(10, title="ammount", description="max ammount of users to return"),
    token: str = Header(...),
):
    """
    This function returns the recommended users for a user.
    """
    try:
        user = get_user_from_token(token)
        recommended_users_db = get_recommended_accounts_for_a_user(
            int(user.get("id")), offset, amount
        )
        users = generate_response_recommended_users_from_db(recommended_users_db)
        return users
    except UserIsPrivate as error:
        raise HTTPException(status_code=403, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error
