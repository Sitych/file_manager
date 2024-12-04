from sqlalchemy import Integer, Column, String
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class UploadingFile(Base):
    __tablename__ = "uploading_files"
    id = Column(String, primary_key=True)
    size = Column(Integer, nullable=True)
    extension = Column(String)
    name = Column(String, nullable=True)
    enctype = Column(String, nullable=True)
