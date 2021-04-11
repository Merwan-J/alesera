from mongoengine import *
import datetime 



class JobType(Document):
    name = StringField()
    keys = ListField(StringField())
    meta = {'db_alias': 'jobtype-db-alias'}
