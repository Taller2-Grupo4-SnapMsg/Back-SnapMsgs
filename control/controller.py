from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from repository.tables.tables import *
from pydantic import BaseModel

from repository.queries.queries import * 

from datetime import datetime
POST_NOT_FOUND = 404
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
        All x posts made by that user. If user made less than x posts, all the posts will be returned.
    
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
        All x posts made in general. If there are less than x posts created, all the posts will be returned.
    
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
        All x posts made in general. If there are less than x posts created, all the posts will be returned.
    
    Raises:
        -
    """
    try:
        delete_post(id)
        return {"message": "Post deleted successfully"}
    except KeyError:
        raise HTTPException(status_code=POST_NOT_FOUND, detail="Post doesnt exist")