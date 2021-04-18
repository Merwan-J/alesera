from mongoengine import *
import datetime 


class Demanders(Document):
    category = StringField()
    demanders = IntField(default=0)
    meta = {'db_alias': 'demanders-db-alias'}

    
