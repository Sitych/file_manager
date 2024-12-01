#!/usr/bin/env python3

from copy import deepcopy

import uvicorn
from fastapi import FastAPI

from app.routers.upload import upload
from app.config import Config

app = FastAPI()

app.include_router(upload.router)

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
