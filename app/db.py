# app/db.py
import mongoengine as me
from app.core.config import settings

def init_db():
    me.connect(host=settings.MONGO_URI)
