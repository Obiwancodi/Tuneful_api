import os.path

from flask import url_for
from sqlalchemy import Column, Integer, String, Sequence, ForeignKey
from sqlalchemy.orm import relationship

from tuneful import app
from database import Base, engine
class File(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key = True)
    file_name = Column(String(250), nullable = False)
    song = relationship("Song", uselist = False, backref = "storage")
    
    def as_dictionary(self):
        file_dict = {
            "id": self.id,
            "file_name": self.file_name
            }
        return file_dict
    
    
    
    
class Song(Base):
    
    __tablename__ = "songs"
    id = Column(Integer, primary_key=True)
    thing = Column(Integer, ForeignKey('files.id'), nullable = False)
    def as_dictionary(self):
        song = {
            "id": self.id,
            "file": self.storage.as_dictionary()
            }
        return song
    
    
    

