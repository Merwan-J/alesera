from mongoengine import *
import datetime 


class Post(Document):
    message_id = IntField()
    date_posted = DateField(default=datetime.datetime.now)
    category= StringField()
    job_title = StringField()
    job_type = StringField()
    description = StringField()
    company = StringField(required=False)
    job_status = StringField(default='open')
    from_chat_id = IntField()
    meta = {'db_alias': 'post-db-alias'}
