import os.path
import json

from flask import request, Response, url_for, send_from_directory
from werkzeug.utils import secure_filename
from jsonschema import validate, ValidationError

import models
import decorators
from tuneful import app
from database import session
from utils import upload_path

file_schema = {
    "type": "object",
        "file": {
            "id": { "type": "integer"}
        }  
    
}   



@app.route("/api/songs", methods = ["GET"])
def get_songs():
    """Get a list of songs"""
    
    songs = session.query(models.Song)
    
    data = json.dumps([song.as_dictionary() for song in songs])
    
    return Response(data, 200, mimetype="application/json")


@app.route("/api/songs", methods = ["POST"])
def post_songs():
    """Add a song"""
    
    data = request.json
    
    
    try:
        validate(data, file_schema)
    except ValidationError as error:
        data = {"message": error.message}
        return Response(json.dumps(data), 422, mimetype = "application/json")
    
    if session.query(models.File).filter(models.File.id == data["file"]["id"]):
        a_song = models.Song(thing=data["file"]["id"])
        session.add(a_song)
        session.commit()
    else:
        return Response(json.dumps(data), 400, mimetype = "application/json")
        
    data = json.dumps(a_song.as_dictionary())
    return Response(data, 201,
                    mimetype="application/json")

@app.route("/api/songs/<int:id>", methods = ["DELETE"])
def delete_song(id):
    """Delete song"""
    
    song = session.query(models.Song).get(id)
    
    if not song:
        message = "Could not find post with id {}".format(id)
        data = json.dumps({"message": message})
        return Response(data, 404, mimetype="application/json")
    
    session.delete(song)
    session.commit()
    song = session.query(models.Song).get(id)
    data = json.dumps(song)
    return Response(data, 200, mimetype="application/json")

@app.route("/api/songs/<int:id>", methods = ["PUT"])
def edit_song(id):
    """Edit Song"""
    
    song = session.query(models.Song).get(id)
    
    if not song:
        message = "Could not find post with id {}".format(id)
        data = json.dumps({"message": message})
        return Response(data, 404, mimetype="application/json")
    
    data = request.json
    
    try:
        validate(data, file_schema)
    except ValidationError as error:
        data = {"message": error.message}
        return Response(json.dumps(data), 422, mimetype = "application/json")
    
    if session.query(models.File).filter(models.File.id == data["file"]["id"]):
        song = models.Song(thing=data["file"]["id"])
        session.commit()
        
    song = session.query(models.Song).get(id)
    data = json.dumps(song.as_dictionary())
    
    return Response(data, 201,
                    mimetype="application/json")

@app.route("/uploads/<filename>", methods=["GET"])
def uploaded_file(filename):
    return send_from_directory(upload_path(), filename)


@app.route("/api/files", methods=["POST"])
@decorators.require("multipart/form-data")
@decorators.accept("application/json")
def file_post():
    file = request.files.get("file")
    if not file:
        data = {"message": "Could not find file data"}
        return Response(json.dumps(data), 422, mimetype="application/json")

    filename = secure_filename(file.filename)
    db_file = models.File(filename=filename)
    session.add(db_file)
    session.commit()
    file.save(upload_path(filename))

    data = db_file.as_dictionary()
    return Response(json.dumps(data), 201, mimetype="application/json")