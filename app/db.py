from typing import List

from sqlalchemy.orm import Session
from sqlalchemy import create_engine, insert

from .models import UploadingFile
from app.config import Config


engine = create_engine(Config.upload_config().db_url)


def get_session():
    with Session(engine) as session:
        yield session


def insert_files_metadata(session: Session, data: List[dict]):
    session.execute(
        insert(UploadingFile), data
    )
    session.commit()
