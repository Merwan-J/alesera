from mongoengine import *
import datetime


class Seeker(Document):
    objects = QuerySetManager()
    user_id = IntField(unique=True)
    username = StringField(required=False)
    date_registered = DateField(default=datetime.datetime.now)
    phone_number = IntField(required=False)
    job_type = StringField(required=True)
    jobs_seen = ListField(ObjectIdField(),required=False)
    jobs_not_seen = ListField(ObjectIdField(),required=False)
    last_message_id = IntField(required=False)
    meta = {'db_alias': 'user-db-alias'}
    