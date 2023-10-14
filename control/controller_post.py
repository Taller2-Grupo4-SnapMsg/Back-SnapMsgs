"""
    Fast API
"""
from fastapi import HTTPException, Header, APIRouter
import httpx
from datetime import datetime

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.queries_post import *

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.queries_repost import *

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.queries_like import *

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.queries_global import *

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from control.common_setup import *

router = APIRouter()

# ------------ POST  ------------

@router.post("/posts", tags=["Posts"])
async def api_create_post(post: PostCreateRequest, token: str = Header(...)):
    user = await get_user_from_token(token)
    
    created_post = create_post(int(user.get("id")), post.content, post.image)
    print("PASA CREAR POST")
    # Asocia etiquetas al post
    try:
        create_hashtag(created_post.id, post.hashtags)  # Convierte el conjunto a lista
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al crear etiquetas")
    
    return {"message": "Post created successfully"}

# # ------------- GET ----------------


@router.get("/posts", tags=["Posts"])
async def api_get_posts(token: str = Header(...)):
    """
    Gets all the posts.

    Returns: List of Posts

    """
    _ = await get_user_from_token(token)
    posts_db = get_all_posts_with_details()
    posts = generate_response_posts_from_db(posts_db)
    return posts


@router.get("/posts/{id}", tags=["Posts"])
async def api_get_post_by_id(id: int, token: str = Header(...)):
    """
    Gets the post with the id

    Args: Id of the post
    Returns: The post with that Id
    Raises: HTTPEXCEPTION with code 404 if post not found
    """
    user = await get_user_from_token(token)
    posts_db = get_post_by_id_global(int(user.get("id")), id)
    posts = generate_response_posts_from_db(posts_db)
    return posts


# pylint: disable=C0103, W0622
@router.get("/posts/user/", tags=["Posts"])  # ANDA
async def api_get_posts_user_by_token(token: str = Header(...)):
    """   
    Gets all posts from a user by token

    Returns: All posts made by that user
    """
    user = await get_user_from_token(token)
    posts_db = get_post_from_user_b_to_user_a(int(user.get("id")), 
                                              int(user.get("id")))
    posts = generate_response_posts_from_db(posts_db)
    return posts


# pylint: disable=C0103, W0622
@router.get("/posts/user/{user_id}", tags=["Posts"])
async def api_get_posts_by_user_id(user_id: int, token: str = Header(...)):
    """
    Gets all posts from a user by id

    Returns: All posts made by that user
    """
    _ = await get_user_from_token(token)
    user = await get_user_from_token(token)
    posts_db = get_post_from_user_b_to_user_a(int(user.get("id")), user_id)
    posts = generate_response_posts_from_db(posts_db)
    return posts

# pylint: disable=C0103, W0622
@router.get("/posts/follow/{date_str}/n/{n}", tags=["Posts"])
async def api_get_posts_users_that_I_follow(n: int, 
                                            date_str: str,
                                            token: str = Header(...)):
    """
    Gets all posts from a user by id

    Returns: All posts made by that user
    """
    date = datetime.strptime(date_str, '%Y-%m-%d_%H:%M:%S')
    user = await get_user_from_token(token)
    posts_db = get_posts_from_users_followed_by_user_a(int(user.get("id")), n, date)
    posts = generate_response_posts_from_db(posts_db)
    return posts

# pylint: disable=C0103, W0622
@router.get("/posts/follow/post_reposts/{date_str}/n/{n}", tags=["Posts"])
async def api_get_posts_users_that_I_follow(n: int, 
                                            date_str: str,
                                            token: str = Header(...)):
    """
    Gets all posts from a user by id

    Returns: All posts made by that user
    """
    date = datetime.strptime(date_str, '%Y-%m-%d_%H:%M:%S')
    user = await get_user_from_token(token)
    posts_db = get_posts_and_reposts_from_users_followed_by_user_a(int(user.get("id")), n, date)
    posts = generate_response_posts_from_db(posts_db)
    return posts

# pylint: disable=C0103, W0622
@router.get("/posts/interest/{date_str}/n/{n}", tags=["Posts"])
async def api_get_posts_users_interest(n: int, 
                                            date_str: str,
                                            token: str = Header(...)):
    """
    Gets all posts from a user by id

    Returns: All posts made by that user
    """
    date = datetime.strptime(date_str, '%Y-%m-%d_%H:%M:%S')
    user = await get_user_from_token(token)
    posts_db = get_public_posts_user_is_interested_in(int(user.get("id")), n, date)
    posts = generate_response_posts_from_db(posts_db)
    return posts


## ------- PUT ---------

@router.put("posts", tags=["Posts"])
async def api_put_posts(token: str = Header(...)):
    """
    Edits the post sent in the request body 

    Args: amount of posts to search

    Returns: All x posts made in general. If there are less
    than x posts created, all the posts will be returned.
    """ 
    response = await get_user_from_token(token)
    # chequear si funciona
    modified_post = PostToEdit(**response.json())
    ## call function
    put_post(modified_post)
    return {"message": "Post edited successfully"}


## ------- DELETE ---------


@router.delete("/post/{id}", tags=["Posts"])
async def api_delete_post(id: int, token: str = Header(...)):
    """
    Deletes the post with the id
    """
    _ = await get_user_from_token(token)
    delete_post(id)
    return {"message": "Post deleted successfully"}
