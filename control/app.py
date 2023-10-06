"""
Set up for the app class
"""


from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from control.controller_like import router as router_like
from control.controller_post import router as router_post

tags_metadata = [
    {"name": "Likes", "description": "Endpoints Likes"},
    {"name": "Posts", "description": "Endpoints Post"},
]

origins = ["*"]

app = FastAPI()

# app.include_router(like_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router_like, prefix="")
app.include_router(router_post, prefix="")
