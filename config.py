import os

class Config:
    SECRET_KEY = os.urandom(24)  # Secret key for sessions
    UPLOAD_FOLDER = 'static/uploads'
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Max image size: 16MB
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disable modification tracking to save resources
    SQLALCHEMY_DATABASE_URI = 'sqlite:///users.db'  # Path to the SQLite database
