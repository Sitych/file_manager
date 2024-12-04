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

    def __repr__(self):
        return f"UploadingFile(id={self.id}, size={self.size}, extension={self.extension}, name={self.name}, self.enctype={self.enctype})"
