# app/models.py
import mongoengine as me
import datetime

class SuppressedEmail(me.Document):
    email = me.StringField(required=True, unique=True)
    created_at = me.DateTimeField(default=datetime.datetime.utcnow)

    meta = {"collection": "suppressed_emails"}
