from fastapi import APIRouter, Header
from repository.queries.queries_repost import *
from control.common_setup import *

router = APIRouter()

@router.post("/reposts", tags=["Reposts"])
async def api_create_repost(post_id: int, token: str = Header(...)):
    user = await get_user_from_token(token)
    create_repost(post_id, user.get("id"))
    return {"message": "Repost created successfully"}


@router.get("/reposts/post/{post_id}", tags=["Reposts"])
async def get_reposts(post_id: int, token: str = Header(...)):
    user = await get_user_from_token(token)
    users = get_reposts_from_post(post_id)
    return generate_response_users_with_user_from_back_user(users)


@router.get("/reposts/post/{post_id}/count", tags=["Reposts"])
async def get_number_of_reposts(post_id: int, token: str = Header(...)):
    user = await get_user_from_token(token)
    reposts = get_the_number_of_reposts_of_a_post(post_id)
    return reposts


@router.get("/reposts/user/", tags=["Reposts"])
async def get_reposts_user(token: str = Header(...)):
    user = await get_user_from_token(token)
    posts = get_the_posts_reposted_by_the_user(user.get("id"))
    return generate_response_posts_with_users_from_db(posts)


@router.delete("/reposts/user/post/{post_id}", tags=["Reposts"])
async def api_delete_respost(post_id: int, token: str = Header(...)):
    user = await get_user_from_token(token)
    delete_repost(user.get("id"), post_id)
    return {"message": "Repost deleted successfully"}


@router.get("/reposts", tags=["Reposts"])
def get_all_resposts():
    all_reposts = get_all_the_reposts()
    reposts_data = [
        {"user_id": respost.user_id, "post_id": respost.id_post} for respost in all_reposts
    ]
    return reposts_data