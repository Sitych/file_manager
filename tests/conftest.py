import shutil
from pathlib import Path
from typing import Any
from typing import Generator
from enum import Enum

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base
from app.db import get_session, insert_files_metadata
from app.routers import download, upload
from app.config import Config

BASE_PATH = Path(__file__).parent
TEST_DATA_DIR = BASE_PATH / 'data'
TEST_STORAGE_DIR = BASE_PATH / 'storage_dir'


class Filenames(Enum):
    SUCCESS = 'success.txt'
    EMPTY = 'empty.txt'
    NO_EXT = 'no_extension'
    TOO_LARGE = 'too_large.txt'


def send_file(filename: str, client: FastAPI, send_filename: bool = True):
    with open(TEST_DATA_DIR / filename, 'rb') as file:
        file_req = {'file': file}
        header = {}
        if send_filename:
            header['filename'] = filename
        res = client.post("/upload", headers=header, files=file_req)
        return res


def start_application():
    app = FastAPI()
    app.include_router(upload.router)
    app.include_router(download.router)
    return app


SQLALCHEMY_DATABASE_URL = Config.upload_config().db_url
engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

SessionTesting = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def app() -> Generator[FastAPI, Any, None]:
    """
    Create a fresh database on each test case.
    """
    Base.metadata.create_all(engine)
    _app = start_application()
    yield _app
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def db_session(app: FastAPI) -> Generator[SessionTesting, Any, None]:
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionTesting(bind=connection)
    yield session  # use the session in tests.
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(
    app: FastAPI, db_session: SessionTesting
) -> Generator[TestClient, Any, None]:

    def _get_test_session():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_session] = _get_test_session
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope='function')
def uuid(client: TestClient):
    res = send_file(Filenames.SUCCESS.value, client)
    return res.json()[Filenames.SUCCESS.value]


@pytest.fixture(scope='module')
def create_storage_dir():
    TEST_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    yield
    print("DELETE DIR")
    # shutil.rmtree(TEST_DATA_DIR)
