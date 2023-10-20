"""
Queries for creating, updating and deleting posts
"""
from sqlalchemy.exc import IntegrityError

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.common_setup import *

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.queries_hashtags import *
from repository.queries.queries_likes import *
from repository.queries.queries_reposts import *

# pylint: disable=C0114, W0401, W0614, E0401
from repository.errors import (
    PostNotFound,
    DatabaseError,
    UserWithouPermission,
)

# pylint: disable=C0114, W0401, W0614, E0401
from repository.tables.posts import Post, Content


def create_post(user_id, text, image, hashtags):
    """
    Create a post made by the user_id, with that content and image
    """
    try:
        content = Content(
            text=text,
            image=image
        )

        session.add(content)  # Add content to the session
        session.flush()  # This will insert both content and post into the database
        
        post = Post(
            user_poster_id = user_id,
            user_creator_id = user_id,
            content_id = content.content_id,
        )
        session.add(post)
        session.flush()
        
        create_hashtags(content.content_id, hashtags) 
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise DatabaseError from error

def update_post(post_id, user_id, text, image, hashtags):
    """
    Updates posts contents, image and hashtags
    """
    try:
        post = (session.query(Post)
                            .filter(Post.post_id == post_id)
                            .first())
        if post is None:
            raise PostNotFound()

        #user wants to modify a post that they didnt create --> not allowed
        if post.user_creator_id != user_id:
            raise UserWithouPermission()
        
        #user wants to modify a repost --> not allowed
        if post.user_creator_id != post.user_poster_id:
            raise UserWithouPermission()
        
        content = (session.query(Content)
                            .filter(Content.content_id == post.content_id)
                            .first())
        content.text = text
        content.image = image

        delete_hashtags_for_content(content.content_id)
        create_hashtags(content.content_id, hashtags)
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise DatabaseError from error
    

def delete_post(post_id, user_id):
    """
    Deletes the post and all the reposts made of that post, as well as the hashtags and likes
    """

    try:
        original_post = session.query(Post).filter(Post.post_id == post_id).first()
        if original_post is None:
            raise PostNotFound()
        
        #trying to delete a post that was not made by this user
        if original_post.user_poster_id != user_id: 
            raise UserWithouPermission()
        
        #trying to delete a repost --> wrong endpoint
        if original_post.user_creator_id != user_id: 
            raise UserWithouPermission()

        delete_reposts_for_content(original_post.content_id)
        delete_hashtags_for_content(original_post.content_id)
        delete_likes_for_content(original_post.content_id)
        
        content_to_delete = session.query(Content).filter(Content.content_id == original_post.content_id).first()
        session.delete(content_to_delete)
        session.delete(original_post)
        
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise DatabaseError from error
