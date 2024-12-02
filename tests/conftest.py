import shutil
from pathlib import Path
from typing import Any
from typing import Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.routers.upload.models import Base
from app.routers.upload.db import get_session
from app.routers.upload.upload import router
from app.config import Config

BASE_PATH = Path(__file__).parent
TEST_DATA_DIR = BASE_PATH / 'data'
TEST_STORAGE_DIR = BASE_PATH / 'storage_dir'


def start_application():
    app = FastAPI()
    app.include_router(router)
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


@pytest.fixture(scope='module')
def create_storage_dir():
    TEST_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    yield
    print("DELETE DIR")
    # shutil.rmtree(TEST_DATA_DIR)