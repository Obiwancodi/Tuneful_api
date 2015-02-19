import unittest
import os
import shutil
import json
from urlparse import urlparse
from StringIO import StringIO

import sys; print sys.modules.keys()
# Configure our app to use the testing databse
os.environ["CONFIG_PATH"] = "tuneful.config.TestingConfig"

from tuneful import app
from tuneful import models
from tuneful.utils import upload_path
from tuneful.database import Base, engine, session

class TestAPI(unittest.TestCase):
    """ Tests for the tuneful API """

    def setUp(self):
        """ Test setup """
        self.client = app.test_client()

        # Set up the tables in the database
        Base.metadata.create_all(engine)

        # Create folder for test uploads
        os.mkdir(upload_path())

    def tearDown(self):
        """ Test teardown """
        session.close()
        # Remove the tables and their data from the database
        Base.metadata.drop_all(engine)

        # Delete test upload folder
        shutil.rmtree(upload_path())
        
    def testNosongs(self):
        response = self.client.get("/api/songs")
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        
        data = json.loads(response.data)
        self.assertEqual(data, [])

    def testGetsongs(self):
        fileA = models.File()
        fileB = models.File()
        fileA.file_name ="test1"
        fileB.file_name = "test2"
        
        songA = models.Song()
        songB = models.Song()
        
        fileA.song = songA
        fileB.song = songB
        session.add_all([fileA, fileB, songA, songB])
        session.commit()
        
        response = self.client.get("/api/songs")
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)
        
        songA = data[0]
        self.assertEqual(songA["id"], 1)
        
        songB = data[1]
        self.assertEqual(songB["id"], 2)

    def testNewSong(self):
        """ Posting a new song """
        fileA = models.File()
        fileA.file_name ="test1"
        session.add(fileA)
        session.commit()
        
        data = {
            "file": {
                "id": 1,
                         
            }
        }
        response = self.client.post("/api/songs",
                  data=json.dumps(data),
                  content_type="application/json"
                  )
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.mimetype, "application/json")      
        
        data = json.loads(response.data)
        self.assertEqual(data["id"], 1)
        
        song = session.query(models.Song).get(1)
        self.assertEqual(1, song.storage.id)
        
    def testDeleteSong(self):
        """Test Delete song"""
        fileA = models.File()
        fileA.file_name = "test1"
        a_song = models.Song()
        fileA.song = a_song
        session.add(fileA,a_song)
        session.commit()
        
        songs = session.query(models.Song).all()
        self.assertEqual(len(songs), 1)
        
        response = self.client.delete("/api/songs/{}".format(a_song.id))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        songs = session.query(models.Song).all()
        self.assertEqual(len(songs),0)
        
    def testEditSong(self):
        """Test Edit Song"""
        fileA = models.File()
        fileA.file_name ="test1"
        session.add(fileA)
        session.commit()
        
        data = {
            "file": {
                "id": 1,
                         }
        }
        
        a_song = models.Song()
        fileA.song = a_song
        session.add(a_song)
        session.commit()
        
        songs = session.query(models.Song).all()
        self.assertEqual(len(songs), 1)
        
        
        song = session.query(models.Song).get(1)
        self.assertEqual(1, song.storage.id)
        
        
        response = self.client.put("/api/songs/{}".format(a_song.id),
            data=json.dumps(data),
            content_type="application/json")
        
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.mimetype, "application/json")
        
        songs = session.query(models.Song).all()
        self.assertEqual(len(songs), 1)
        
        data = json.loads(response.data)
        self.assertEqual(data["id"], 1)
        
        song = session.query(models.Song).get(1)
        self.assertEqual(1, song.storage.id)
        