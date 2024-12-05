from .conftest import Filenames, send_file
from mock import patch
import pytest
from fastapi import FastAPI, status


def check_file(filename: str, client: FastAPI, status_code: int, send_filename: bool = True):
    res = send_file(filename, client, send_filename)
    assert res.status_code == status_code


def test_no_filename(client: FastAPI, create_storage_dir):
    check_file(
        filename=Filenames.SUCCESS.value,
        client=client,
        send_filename=False,
        status_code=status.HTTP_400_BAD_REQUEST
    )

@patch('app.config.GB', 1)
def test_too_large(client: FastAPI):
    check_file(
        filename=Filenames.TOO_LARGE.value,
        client=client,
        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
    )


@pytest.mark.parametrize("filename", [Filenames.NO_EXT.value, Filenames.SUCCESS.value])
def test_successful(client: FastAPI, filename: str):
    status_code = status.HTTP_200_OK
    check_file(
        filename=filename,
        client=client,
        status_code=status_code,
    )
