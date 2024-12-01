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
from app.config import Config
from app.lib.utils import MaxBodySizeException, MaxBodySizeValidator


router = APIRouter()


async def upload_file_from_request(request: Request, config: Config):
    body_val = MaxBodySizeValidator(max_size=config.max_body_size)
    # cloud = Cloud(cloud_config)

    filename = request.headers.get("filename")

    if filename is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The header field for filename is missing",
        )

    filename = unquote(filename)
    uuid_ = str(uuid.uuid1())
    file_path = Path(config.storage_dir) / uuid_
    parser = StreamingFormDataParser(headers=request.headers)
    file_ = FileTarget(file_path, validator=MaxSizeValidator(config.max_file_size))
    parser.register("file", file_)
    parser.register("data", ValueTarget())

    try:
        async for chunk in request.stream():
            body_val(chunk)
            parser.data_received(chunk)
            # await cloud.uplod_file_by_chunks(chunk, uuid_)
    except ClientDisconnect:
        print("Client disconnect")
    except MaxBodySizeException as exp:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"The request's body size ({exp.body_len}) is more than the server limit ({config.max_body_size})",
        )
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"The file's size is more than server limit ({config.max_file_size})",
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
    return (uuid_, body_val.body_len)


@router.post("/upload")
async def upload_file(request: Request):
    config = Config.upload_config()
    uuid_, body_len = await upload_file_from_request(request, config)
    return HTMLResponse("<h2>Dataset was uploaded</h2>", status_code=status.HTTP_200_OK)