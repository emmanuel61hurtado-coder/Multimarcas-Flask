import os
import secrets
class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///taller.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = secrets.token_urlsafe(24)