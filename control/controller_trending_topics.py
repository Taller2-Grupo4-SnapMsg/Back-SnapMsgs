import asyncio
from fastapi import FastAPI, WebSocket, BackgroundTasks
from fastapi.responses import HTMLResponse

from repository.queries.queries_trending_topics import *

app = FastAPI()

async def send_trending_topics(websocket: WebSocket):
    while True:
        trending_topics = get_trending_topics(10, 0)
        await websocket.send_text(f"Los temas populares son: {', '.join(trending_topics)}")
        await asyncio.sleep(3600)

@app.websocket("/ws/trending")
async def websocket_endpoint(websocket: WebSocket, background_tasks: BackgroundTasks):
    await websocket.accept()
    background_tasks.add_task(send_trending_topics, websocket)
