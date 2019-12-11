from flask_login import UserMixin
from werkzeug.security import generate_password_hash
import random
import re
import uuid
from bson.objectid import ObjectId
import const
from mongoengine import Document, DateTimeField, StringField, ReferenceField, ListField, \
    IntField, FloatField, URLField, Q, DynamicDocument, BooleanField
import mongoengine as db

db.connect('mainData')

class User(UserMixin, Document):
    email = StringField(required=True, unique=True, max_length=254)
    password_hash = StringField(required=True)
    session_token = StringField(required=True, unique=True)
    role = StringField(choices=const.User.roles, required=True)
    level = StringField(choices=const.User.levels, required=True)
    progress=FloatField(default=0)
    group=ListField(IntField())
    proficiency=StringField()


    def get_id(self):
        return self.session_token

    def is_admin(self):
        return self.role == "teacher"

    def is_guest(self):
        return self.role == "student"


    def can_comment(self):
        return self.is_authenticated

    def dictify(self):
        return {
            'mongoid': str(self.pk),
            'email': self.email,
            'role': self.role,
            'level': self.level
        }

    @staticmethod
    def get_user_from_mongoid(mongoid):
        return User.objects(pk=ObjectId(mongoid)).first()

    @staticmethod
    def get_user_from_group(group_id):
        return User.objects(role='student',group=group_id)
    @staticmethod
    def get_user_from_session_token(session_token):
        return User.objects(session_token=session_token).first()

    @staticmethod
    def create_root(email, password):
        password_hash = generate_password_hash(password)
        session_token = str(uuid.uuid4())
        user = User(email=email, password_hash=password_hash, session_token=session_token, role="teacher", level="admin")
        return user.save()

    @staticmethod
    def create(email, password, role, level):
        password_hash = generate_password_hash(password)
        session_token = str(uuid.uuid4())
        user = User(email=email, password_hash=password_hash, session_token=session_token, role=role, level=level)
        return user.save()

    def update(self, password, role, level):
        if password is not "":
            self.password_hash = generate_password_hash(password)
            self.session_token = str(uuid.uuid4())  # this will logout existing users
            print(self.session_token)
        self.role = role
        self.level = level
        return self.save()


class Assignment(Document):

    heading=StringField()
    text=StringField()
    user=ReferenceField(User,required=True)
    comments=ListField(StringField)
    comments_by=ListField(ReferenceField(User))
    keyword=ListField(StringField,required=True)
    reaction=ListField(StringField)
    hilarious=ListField(ReferenceField(User))
    well_written=ListField(ReferenceField(User))
    amazing_story=ListField(ReferenceField(User))

    grammar_king=ReferenceField(User)

    group=IntField()
    assignment_id=IntField()

    @staticmethod
    def create(heading,text,user,keyword,group,assignment_id):

        Assignment(heading=heading,text=text,user=user,keyword=keyword,group=group,assignment_id=assignment_id)
        assign=Assignment.save()
        return assign

    @staticmethod
    def create_assignment(heading,text,keyword,group_number):
        #only created by teacher.

        Users=User.get_user_from_group(group_number)
        #create assignments for them

        assignment_id=random.randint(0,100)
        for user in Users:
            Assignment.create(heading,text,user,keyword,group_number,assignment_id)


        return assignment_id

    @staticmethod
    def submit_assigment(text,user,group_number,assignment_id):

        assignment=Assignment.objects(user=user,group_number=group_number,assignment_id=assignment_id)
        if assignment:
            assignment.update(text=text)
        else:
            return 'assignment not found'


