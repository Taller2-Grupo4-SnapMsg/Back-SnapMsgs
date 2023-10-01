"""
Archivo con algunas pruebas de la base de datos
"""
from repository.queries.queries import create_post, get_posts, get_post_by_id

USER_ID = 58
CONTENT = "primer postttt"
IMAGE = "jjdjdjd"
create_post(USER_ID, CONTENT, IMAGE)

CONTENT = "otro postttt!"
IMAGE = "jjdjdjdasdada"
create_post(USER_ID, CONTENT, IMAGE)

posts = get_posts()
for post in posts:
    print(f"User_ID: {post.user_id}, Posted at: {post.posted_at}, Content: {post.content}")

post = get_post_by_id(10)
if post:
    print(f"User_ID: {post.user_id}, Posted at: {post.posted_at}, Content: {post.content}")
else:
    print("No se encontró el post")


