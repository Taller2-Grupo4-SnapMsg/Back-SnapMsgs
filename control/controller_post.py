"""
    Fast API
"""
from fastapi import HTTPException, Header, APIRouter
import httpx

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

# ------------ Function Auxiliar ------------

def generate_posts_with_info():
    """
    Retrieves all posts with their corresponding user info, likes, and reposts.

    Returns:
        List[dict]: A list of dictionaries representing each post with user info,
        likes count, and reposts count.
    """
    posts = get_posts()
    
    posts_info = []
    for post, user in posts:
        likes_count = get_the_number_of_likes(post.id)
        reposts_count = get_the_number_of_reposts_of_a_post(post.id)
        
        post_info = generate_post_from_db(post, user, likes_count, reposts_count)        
        posts_info.append(post_info)
    
    return posts_info

# ------------ POST  ------------


@router.post("/posts", tags=["Posts"])
async def api_create_post(post: PostCreateRequest, token: str = Header(...)):
    """
    Creates a new post

    Args: post (PostCreateRequest): The post to create.
    Returns: Post: The post that was created.

    """
    user = await get_user_from_token(token)
    create_post(int(user.get("id")), post.content, post.image)
    return {"message": "Post created successfully"}

# # ------------- GET ----------------


# @router.get("/posts", tags=["Posts"])
# async def api_get_posts(token: str = Header(...)):
#     """
#     Gets all the posts.

#     Returns: List of Posts

#     """
#     _ = await get_user_from_token(token)
#     posts_db = get_all_posts_with_details()
#     posts = generate_response_posts_from_db(posts_db)
#     return posts

@router.get("/posts", tags=["Posts"])
async def api_get_posts(token: str = Header(...)):
    """
    Gets all the posts.

    Returns: List of Posts

    """
    _ = await get_user_from_token(token)
    posts = generate_posts_with_info()
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
    posts_db = get_post_from_user_b_to_user_a(int(user.get("id")), id)
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
    posts_db = get_posts_from_users_followed_by_user_a(int(user.get("id")))
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


@router.get("/posts/user/amount/{x}", tags=["Posts"])
async def api_get_x_newest_posts_by_user(x: int, token: str = Header(...)):
    """
    Gets x amount of newest posts made by that user (the owner of the token)

    Args: amount of posts to search

    Returns: All x posts made by that user. If user made less
    than x posts, all the posts will be returned.
    """
    user = await get_user_from_token(token)
    posts = get_x_newest_posts_by_user(int(user.get("id")), x)
    return generate_response_posts_with_user_from_back_user(posts, user)



@router.get("/posts/amount/{x}", tags=["Posts"])
async def api_get_x_newest_posts(x: int, token: str = Header(...)):
    """
    Gets x amount of newest posts made in general

    Args: amount of posts to search

    Returns: All x posts made in general. If there are less
    than x posts created, all the posts will be returned.
    """
    _ = await get_user_from_token(token)
    posts = get_x_newest_posts(x)
    return generate_response_posts_with_users_from_db(posts)

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
