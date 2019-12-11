from flask_login import UserMixin
from werkzeug.security import generate_password_hash
import random
import re
import json
import uuid
from bson.objectid import ObjectId
import const
from mongoengine import Document, DateTimeField, StringField, ReferenceField, ListField, \
    IntField, FloatField, URLField, Q, DynamicDocument, BooleanField
import mongoengine as db
import datetime

db.connect('mainData')


class User(UserMixin, Document):
    email = StringField(required=True, unique=True, max_length=254)
    password_hash = StringField(required=True)
    session_token = StringField(required=True, unique=True)
    role = StringField(choices=const.User.roles, required=True)
    level = StringField(choices=const.User.levels, required=True)
    progress = FloatField(default=0)
    group = ListField(IntField())
    proficiency = StringField()

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
        return User.objects(role='student', group=group_id)

    @staticmethod
    def get_user_from_session_token(session_token):
        return User.objects(session_token=session_token).first()

    @staticmethod
    def create_root(email, password):
        password_hash = generate_password_hash(password)
        session_token = str(uuid.uuid4())
        user = User(email=email, password_hash=password_hash, session_token=session_token, role="teacher",
                    level="admin")
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
    header = StringField()
    text = StringField(default="")
    group = IntField()
    active = BooleanField(default=True)
    deadline = DateTimeField()
    created = DateTimeField(default=datetime.datetime.now())
    keyword = ListField(StringField, required=True)

    @staticmethod
    def create(header, tag,day):
        # lets say 7 days
        tag_split=tag.split(',')

        date = (datetime.datetime.now() + datetime.timedelta(days=int(day))).date()
        assign = Assignment(header=header, deadline=date,keyword=staticmethod)
        assign.save()
        return assign

    def get_json(self):
        submissions = len(Post.objects(assignment_id=self.pk, submit=True))

        jstring = ''
        jstring = '{\n"header": ' + json.dumps(self.header) + ',\n' \
                  + '"mongoid": ' + str(self.pk) + ',\n' \
                  + '"text": ' + json.dumps(self.text) + ',\n' \
                  + '"created": ' + json.dumps(self.created.strftime('%Y-%m-%dT%H:%M:%SZ')) + ',\n' \
                  + '"deadline": ' + json.dumps(self.deadline.strftime('%Y-%m-%dT%H:%M:%SZ')) + ',\n' \
                  + '"created": ' + json.dumps(self.created.strftime('%Y-%m-%dT%H:%M:%SZ')) + ',\n' \
                  + '"submission": ' + str(submissions) + "}\n"

        return jstring


class Post(Document):
    text = StringField()
    user = ReferenceField(User, required=True)
    comments = ListField(StringField)
    comments_by = ListField(ReferenceField(User))
    keyword = ListField(StringField, required=True)
    reaction = ListField(StringField)
    hilarious = ListField(ReferenceField(User))
    well_written = ListField(ReferenceField(User))
    amazing_story = ListField(ReferenceField(User))

    grammar_king = ReferenceField(User)

    group = IntField()
    assignment_id = ReferenceField(Assignment)
    submit = BooleanField(default=False)

    @staticmethod
    def create(text, user, keyword, group, assignment_id):

        post = Post(text=text, user=user, keyword=keyword, group=group, assignment_id=assignment_id)
        post.save()
        return post

    # @staticmethod
    # def create_assignment(heading,text,keyword,group_number):
    #     #only created by teacher.
    #
    #     Users=User.get_user_from_group(group_number)
    #     #create assignments for them
    #
    #     assignment_id=random.randint(0,100)
    #     for user in Users:
    #         Assignment.create(heading,text,user,keyword,group_number,assignment_id)
    #
    #
    #     return assignment_id

    @staticmethod
    def submit_assigment(text, user, group_number, assignment_id):

        assignment = Post.objects(user=user, group_number=group_number, assignment_id=assignment_id)
        if assignment:
            assignment.update(text=text, submit=True)
        else:
            return 'assignment not found'


def get_all_assignments():
    assignments = Assignment.objects(active=True)
    json = '{'
    json += '"success": true,"assignments":[ \n'
    for assign in assignments:
        js = assign.get_json()
        json += js + ',\n'
    json = json + ']\n}'
    return json



def make_fake_Assign():
    header='Assignment no: '
    for i in range(1,10):
        header+=str(i)
        Assignment.create(header,text='',group=1)


make_fake_Assign()