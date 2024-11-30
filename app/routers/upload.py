from pathlib import Path
import uuid

from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import HTMLResponse
from streaming_form_data.validators import MaxSizeValidator, ValidationError
from streaming_form_data.parser import StreamingFormDataParser
from streaming_form_data.targets import FileTarget, ValueTarget
from urllib.parse import unquote
from starlette.requests import ClientDisconnect

from app.cloud.cloud import Cloud


MAX_BODY_SIZE = 1024
MAX_FILE_SIZE = 1024
STORAGE_PATH = "/Users/19223700/data/storage_file_manager"


router = APIRouter(prefix="/upload")


class MaxBodySizeException(Exception):
    def __init__(self, body_len: str, *args):
        super().__init__(*args)
        self.body_len = body_len


class MaxBodySizeValidator:
    def __init__(self, max_size: int):
        self.max_size = max_size
        self.body_len = 0

    def __call__(self, chunk: bytes):
        self.body_len += len(chunk)
        if self.body_len >= self.max_size:
            raise MaxBodySizeException(
                self.body_len, "The file's size is over the limit"
            )


async def upload_file_from_request(request: Request, cloud_config: dict):
    body_val = MaxBodySizeValidator(max_size=MAX_BODY_SIZE)
    cloud = Cloud(cloud_config)

    filename = request.headers.get("filename")

    if filename is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The header field for filename is missing",
        )

    filename = unquote(filename)
    uuid_ = str(uuid.uuid1())
    file_path = Path(STORAGE_PATH) / uuid_
    parser = StreamingFormDataParser(headers=request.headers)
    file_ = FileTarget(file_path, validator=MaxSizeValidator(MAX_FILE_SIZE))
    parser.register("file", file_)
    parser.register("data", ValueTarget())

    try:
        async for chunk in request.stream():
            body_val(chunk)
            parser.data_received(chunk)
            await cloud.uplod_file_by_chunks(chunk, uuid_)
    except ClientDisconnect:
        print("Client disconnect")
    except MaxBodySizeException as exp:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"The request's body size ({exp.body_len}) is more than the server limit ({MAX_BODY_SIZE})",
        )
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"The file's size is more than server limit ({MAX_FILE_SIZE})",
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="There was an error uploading the file",
        )

    if not file_.multipart_filename:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="File is missing"
        )


@router.post("/")
async def upload_file(request: Request):
    await upload_file_from_request(request)
    return HTMLResponse("<h2>Dataset was uploaded</h2>", status_code=status.HTTP_200_OK)
