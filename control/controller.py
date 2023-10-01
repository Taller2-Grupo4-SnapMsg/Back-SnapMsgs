from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from repository.tables.tables import *
from pydantic import BaseModel

from repository.queries.queries import * 

from datetime import datetime
POST_NOT_FOUND = 404
USER_NOT_FOUND = 404
LIKE_NOT_FOUND = 404
BAD_REQUEST = 400

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PostResponse(BaseModel):
    """
    This class is a Pydantic model for the response body.
    """

    id: int
    user_id: int
    posted_at: str
    content: str
    image: str

    # I disable it since it's a pydantic configuration
    # pylint: disable=too-few-public-methods
    class Config:
        """
        This is a pydantic configuration so I can cast
        orm_objects into pydantic models.
        """

        orm_mode = True
        from_attributes = True

def generate_post(post):
    """
    This function casts the orm_object into a pydantic model.
    (from data base object to json)
    """
    return PostResponse(
        id=post.id,
        user_id=post.user_id,
        posted_at=str(post.posted_at),
        content=post.content,
        image=post.image,
    )

def generate_response_posts(posts):
    """
    This function casts the list of users into a list of pydantic models.
    """
    response = []
    for post in posts:
        response.append(generate_post(post))
    return response



# ------------ POST  ------------

# Define a Pydantic model for the request body
class PostCreateRequest(BaseModel):
    """
    This class is a Pydantic model for the request body.
    """
    user_id: int
    content: str
    image: str
    

@app.post("/posts")
async def api_create_post(post: PostCreateRequest):
    """
    Creates a new post

    Args:
        post (Post): The post to create.
    
    Returns:
        Post: The post that was created.
    
    Raises:
        -
    """
    create_post(post.user_id, post.content, post.image)
    
    return {"message": "Post created successfully"}




# ------------- GET ----------------

@app.get("/posts")
async def api_get_posts():
    """
    Gets all the posts ever created.
    Use with caution!

    Args:
        -
    
    Returns:
        List of Posts
    
    Raises:
        -
    """

    posts = get_posts()
    return generate_response_posts(posts)

@app.get("/posts/{id}")
async def api_get_post_by_id(id: int):
    """
    Gets the post with the id passed
    Args:
        :param id: Id of the post
    
    Returns:
        The post with that Id
    
    Raises:
        HTTPEXCEPTION with code 404 if post not found
    """
    post = get_post_by_id(id)
    if post is None:
        raise HTTPException(status_code=POST_NOT_FOUND, detail="Post not found")
    return generate_post(post)

#Acá no hacemos diferencia entre si encontramos o no al usuario, directamente
#devolvemos el vector vacío o el vector con elemento
#deberíamos verificar algo más?
@app.get("/posts/user/{id}")
async def api_get_posts_by_user_id(id: int):
    """
    Gets all posts made by that user
    Use with caution!

    Args:
        :param id: Id of the user
    
    Returns:
        All posts made by that user
    
    Raises:
        
    """
    posts = get_posts_by_user_id(id)
    return generate_response_posts(posts)


#TODO
@app.get("/posts/user/{id}/date/{date}")
async def api_get_posts_by_user_and_date(id: int, date: str):
    """
    Gets all posts made by that user that date

    Args:
        :param id: Id of the user
        :param date: Specific date as a string with format "YYYY-MM-DD"
    
    Returns:
        All posts made by that user that date
    
    Raises:
        ValueError: if invalid date format
    """
    try:
        # está comparando YYYY-MM-DD contra YYYY-MM-DD HH-MM-SS que hay en la bdd
        datetime_date = datetime.strptime(date, "%Y-%m-%d")

        post = get_posts_by_user_and_date(id, datetime_date)
        print(post)
        return generate_response_posts(post)
    except ValueError:
        raise HTTPException(status_code=BAD_REQUEST, detail="Invalid date format. Expected format: YYYY-MM-DD")
    
@app.get("/posts/user/{id}/amount{x}")
async def api_get_x_newest_posts_by_user(id: int, x: int):
    """
    Gets x amount of newest posts made by that user

    Args:
        :param id: Id of the user
        :param x: amount of posts to search
    
    Returns:
        All x posts made by that user. If user made less 
        than x posts, all the posts will be returned.
    
    Raises:
        
    """
    if (x <= 0):
        raise HTTPException(status_code=BAD_REQUEST, detail="Amount must be greater than 0")
    
    posts = get_x_newest_posts_by_user(id, x)
    return generate_response_posts(posts)


@app.get("/posts/amount/{x}")
async def api_get_x_newest_posts(x: int):
    """
    Gets x amount of newest posts made in general

    Args:
        :param x: amount of posts to search
    
    Returns:
        All x posts made in general. If there are less 
        than x posts created, all the posts will be returned.
    
    Raises:
        
    """
    if (x <= 0):
        raise HTTPException(status_code=BAD_REQUEST, detail="Amount must be greater than 0")
    
    posts = get_x_newest_posts(x)
    return generate_response_posts(posts)

    
# ------- DELETE ---------

@app.delete("/post/{id}")
async def api_delete_post(id: int):
    """
    Gets x amount of newest posts made in general

    Args:
        :param x: amount of posts to search
    
    Returns:
        All x posts made in general. If there are less than x posts 
        created, all the posts will be returned.
    
    Raises:
        -
    """
    try:
        delete_post(id)
        return {"message": "Post deleted successfully"}
    except KeyError:
        raise HTTPException(status_code=POST_NOT_FOUND, detail="Post doesnt exist")
    

# -------- Likes ---------

# -------- Post -----------

# Define a Pydantic model for the request body
class LikeCreateRequest(BaseModel):
    """
    This class is a Pydantic model for the request body.
    """
    user_id: int
    post_id: int

    # I disable it since it's a pydantic configuration
    # pylint: disable=too-few-public-methods
    class Config:
        """
        This is a pydantic configuration so I can cast
        orm_objects into pydantic models.
        """

        orm_mode = True
        from_attributes = True

def generate_like(like):
    """
    This function casts the orm_object into a pydantic model.
    (from data base object to json)
    """
    return LikeCreateRequest(
        user_id=like.user_id,
        post_id=like.post_id
    )

@app.post("/like")
async def api_create_like(like: LikeCreateRequest):
    """
    Creates a new like

    Args:
        like (Like): The like to create.
    
    Returns:
        Like: The like that was created.
    
    Raises:
        -
    """
    #deberia chequear si existen
    print("entra al controller")
    create_like(like.post_id, like.user_id)
    
    return {"message": "Like created successfully"}

# -------- Get -----------

@app.get("/likes")
def get_all_likes():
    """
    Retrieve all likes in the system.

    This function returns a list of all likes recorded in the system.

    Returns:
        List[Dict[str, int]]: A list of dictionaries, each containing 
        'user_id' and 'post_id' representing a like.

    Raises:
        No exceptions raised.
    """
    all_likes = get_all_the_likes()
    likes_data = [{'user_id': like.user_id, 'post_id': like.id_post} for like in all_likes]
    return likes_data


@app.get("/like/{post_id}")
def get_the_number_of_likes(post_id: int):
    """
    Retrieve the user IDs of users who liked a specific post.

    Given a `post_id`, this function returns a list of user IDs 
    representing users who liked the post.

    Args:
        post_id (int): The ID of the post to retrieve likes for.

    Returns:
        List[int]: A list of user IDs representing users who liked the post.

    Raises:
        HTTPException: If the specified post does not exist, an 
        HTTPException with a 404 status code is raised.
    """
    try:
        likes_list = get_likes_for_a_post(post_id)
        user_ids = [like.user_id for like in likes_list]
        return user_ids
    except PostNotFound as error:
        raise HTTPException(status_code=POST_NOT_FOUND, detail=str(error)) from error
    
@app.get("/like/{post_id}/count")
def get_number_of_likes(post_id: int):
    """
    Get the number of likes for a specific post.

    Args:
        post_id (int): The ID of the post for which you want to get 
        the like count.

    Returns:
        int: The number of likes for the specified post.

    Raises:
        HTTPException: If the post with the specified ID is not found, 
        it will raise an HTTP 404 error.
    """
    try:
        likes = get_likes_count(post_id)
        return likes
    except PostNotFound as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    
# Daba error si le ponia la misma ruta que con post_id  
@app.get("/like/user/{user_id}")
def get_likes_user(user_id: int):
    """
    Retrieve the post IDs that a specific user has liked.

    Given a `user_id`, this function returns a list of post IDs representing 
    the posts that the user has liked.

    Args:
        user_id (int): The ID of the user to retrieve liked posts for.

    Returns:
        List[int]: A list of post IDs representing posts liked by the user.

    Raises:
        HTTPException: If the specified user does not exist, an HTTPException 
        with a 404 status code is raised.
    """
    try:
        liked_posts = get_all_the_likes_of_a_user(user_id)
        post_ids = [like.id_post for like in liked_posts]
        return post_ids
    except UserNotFound as error:
        raise HTTPException(status_code=USER_NOT_FOUND, detail=str(error)) from error
    
    
# -------- Delete -----------

    
@app.delete("/like/{like_id}")
async def api_delete_like(like_id: int):
    """
    Deletes a like by its ID.

    Args:
        like_id (int): The ID of the like to be deleted.

    Returns:
        dict: A message indicating the successful deletion of the like.

    Raises:
        HTTPException: If the specified like does not exist, an 
        HTTPException with a 404 status code is raised.
    """
    try:
        delete_like(like_id)
        return {"message": "Like deleted successfully"}
    except KeyError:
        raise HTTPException(status_code=LIKE_NOT_FOUND, detail="Like doesn't exist")