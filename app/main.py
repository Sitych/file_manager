#!/usr/bin/env python3

import uvicorn
from fastapi import FastAPI

from app.routers import upload, download
from app.config import Config

app = FastAPI()

app.include_router(upload.router)
app.include_router(download.router)


def run_server():

    config = Config.upload_config()
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=config.port,
        loop="asyncio",
        workers=config.workers,
    )


if __name__ == "__main__":
    run_server()
