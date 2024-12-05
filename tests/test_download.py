from .conftest import Filenames, TEST_DATA_DIR
from mock import patch
import pytest
from fastapi import FastAPI, status
import requests

URL_PATH = '/download'


def test_non_existant_file(client: FastAPI):
    uuid = 'non-existance'
    response = client.get(URL_PATH, params={'uuid': uuid})
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json().get(uuid) is not None


def test_streaming_file(client: FastAPI, uuid: str):
    with client.stream('GET', URL_PATH, params={'uuid': uuid}) as response:
        chunks = [chunk for chunk in response.iter_raw(1)]
    assert response.status_code == status.HTTP_200_OK, "The server must return 200 status code"
    assert len(chunks) != 0, "The server must return data"
    assert len(chunks[0]) == 1, "The chunks size must be 1"
    text = b''.join(chunks)
    with open(TEST_DATA_DIR / Filenames.SUCCESS.value, 'rb') as file:
        assert text == file.read(), "The returned data is not equal source data"
