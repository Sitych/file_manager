from pathlib import Path

from fastapi import APIRouter, Request, HTTPException, status, Depends, Header
from fastapi.responses import StreamingResponse, JSONResponse
import aiofiles

from app.config import Config
from app.db import get_session, Session, select_file

CHUNK_SIZE = 1024 * 1024


router = APIRouter()


async def stream_file(path: Path):
    async with aiofiles.open(path, "rb") as f:
        while chunk := await f.read(CHUNK_SIZE):
            yield chunk


@router.get("/download")
async def upload_file(
    uuid: str,
    session: Session = Depends(get_session),
):
    config = Config.upload_config()
    file = select_file(uuid, session)
    file_path = config.storage_dir / file.id
    if not file_path.exists():
        return JSONResponse(
            {uuid: "The file doesnt exist"}, status_code=status.HTTP_404_NOT_FOUND
        )
    return StreamingResponse(
        stream_file(file_path),
        media_type=file.enctype,
        headers={"filename": file.name, "file_size": str(file.size)},
    )
