import os.path

from flask import url_for
from sqlalchemy import Column, Integer, String, Sequence, ForeignKey
from sqlalchemy.orm import relationship

from tuneful import app
from database import Base, engine
class File(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key = True)
    filename = Column(String(250), nullable = False)
    song = relationship("Song", uselist = False, backref = "storage")
    
    def as_dictionary(self):
        file_dict = {
            "id": self.id,
            "name": self.filename,
            "path": url_for("uploaded_file", filename=self.filename)
        }
        return file_dict
    
class Song(Base):
    
    __tablename__ = "songs"
    id = Column(Integer, primary_key=True)
    thing = Column(Integer, ForeignKey('files.id'), nullable = False)
    def as_dictionary(self):
        song = {
            "id": self.id,
            "file": {
                "id": self.storage.id,
                "name": self.storage.filename,
                "path": url_for("uploaded_file", filename=self.storage.filename)
                
            }
            }
        return song
    
    
    

