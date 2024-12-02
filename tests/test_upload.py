from .conftest import TEST_DATA_DIR
from enum import Enum
from mock import patch
import pytest
from fastapi import FastAPI, status


class Filenames(Enum):
    SUCCESS = 'success.txt'
    EMPTY = 'empty.txt'
    NO_EXT = 'no_extension'
    TOO_LARGE = 'too_large.txt'


def send_file(filename: str, client: FastAPI, status_code: int, send_filename: bool = True):
    with open(TEST_DATA_DIR / filename, 'rb') as file:
        file_req = {'file': file}
        header = {}
        if send_filename:
            header['filename'] = filename
        res = client.post("/upload", headers=header, files=file_req)
        assert res.status_code == status_code


def test_no_filename(client: FastAPI, create_storage_dir):
    send_file(
        filename=Filenames.SUCCESS.value,
        client=client,
        send_filename=False,
        status_code=status.HTTP_400_BAD_REQUEST
    )

@patch('app.config.GB', 1)
def test_too_large(client: FastAPI):
    send_file(
        filename=Filenames.TOO_LARGE.value,
        client=client,
        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
    )


@pytest.mark.parametrize("filename", [Filenames.NO_EXT.value, Filenames.SUCCESS.value])
def test_successful(client: FastAPI, filename: str):
    status_code = status.HTTP_200_OK
    send_file(
        filename=filename,
        client=client,
        status_code=status_code,
    )
