from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import create_engine, insert, select

from app.models import UploadingFile
from app.config import Config


engine = create_engine(Config.upload_config().db_url)


def get_session():
    with Session(engine) as session:
        yield session


def insert_files_metadata(session: Session, data: List[dict]):
    session.execute(insert(UploadingFile), data)
    session.commit()


def select_file(uuid: str, session: Session) -> Optional[UploadingFile]:
    data = session.execute(select(UploadingFile).filter_by(id=uuid))
    firest_elem = data.first()
    if firest_elem is None:
        return None
    item: UploadingFile = firest_elem[0]
    session.commit()
    return item
