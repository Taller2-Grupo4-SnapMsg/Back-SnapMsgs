from repository.queries.queries import *
from datetime import datetime

user_id = 58
posted_at = datetime.utcnow()
content = "primer postttt"
image= "jjdjdjd"
create_post(user_id, posted_at, content, image)

posted_at = datetime.utcnow()
content = "otro postttt!"
image= "jjdjdjdasdada"
create_post(user_id, posted_at, content, image)

# se deberían mostrar dos posts por terminal
posts = get_posts()
for post in posts:
   print(f"User_ID: {post.user_id}, Posted at: {post.posted_at}, Content: {post.content}")

#se debería mostrar el segundo post
post = get_post_by_id(10)
if (post):
    print(f"User_ID: {post.user_id}, Posted at: {post.posted_at}, Content: {post.content}")
else:
    print("no lo levanta")
