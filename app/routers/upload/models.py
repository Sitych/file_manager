from sqlalchemy import Integer, Column, create_engine, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
engine = create_engine('postgresql://19223700@localhost/file_manager')


class UploadingFiles(Base):
    __tablename__ = "uploading_files"
    id = Column(String, primary_key=True)
    size = Column(Integer, nullable=True)
    extension = Column(String)
    name = Column(String, nullable=True)
    enctype = Column(String, nullable=True)
