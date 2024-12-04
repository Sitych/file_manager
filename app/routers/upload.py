from pathlib import Path
import uuid

from fastapi import APIRouter, Request, HTTPException, status, Depends, Header
from fastapi.responses import JSONResponse
from streaming_form_data.validators import MaxSizeValidator, ValidationError
from streaming_form_data.parser import StreamingFormDataParser
from streaming_form_data.targets import FileTarget, ValueTarget
from urllib.parse import unquote
from starlette.requests import ClientDisconnect
from sqlalchemy import insert

from app.cloud.cloud import Cloud
from app.config import Config
from app.lib.utils import MaxBodySizeException, MaxBodySizeValidator, parse_content_type
from app.dependences import filename_, fileformat
from app.db import get_session, Session, insert_files_metadata


router = APIRouter()


async def upload_file_from_request(request: Request, config: Config):
    body_val = MaxBodySizeValidator(max_size=config.max_body_size)
    # cloud = Cloud(cloud_config)

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


@router.post("/upload", dependencies=[Depends(filename_), Depends(fileformat)])
async def upload_file(
    request: Request,
    filename: str = Header(...),
    content_type: str = Header(...),
    session: Session = Depends(get_session),
):
    config = Config.upload_config()
    uuid_, body_len = await upload_file_from_request(request, config)
    filename = unquote(filename)
    extension = Path(filename).suffix
    file_format = parse_content_type(content_type)
    meta_data = {
        "id": uuid_,
        "size": body_len,
        "extension": extension,
        "name": filename,
        "enctype": file_format,
    }
    insert_files_metadata(session, [meta_data])
    return JSONResponse({filename: uuid_}, status_code=status.HTTP_200_OK)
