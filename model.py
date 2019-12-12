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
from flask_login import current_user

db.connect('mainData')


class User(UserMixin, Document):
    name = StringField(required=True)
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
    def create(email, password, role, level, name):
        password_hash = generate_password_hash(password)
        session_token = str(uuid.uuid4())
        user = User(email=email, password_hash=password_hash, session_token=session_token, role=role, level=level,
                    name=name)
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
    keyword = ListField(StringField(), required=True)

    @staticmethod
    def create(header, tag, day):
        # lets say 7 days
        print(type(tag))
        tag_split = tag.split(',')

        date = (datetime.datetime.now() + datetime.timedelta(days=int(day))).date()

        assign = Assignment(header=header, deadline=date, keyword=tag_split)
        assign.save()
        return assign

    def get_json(self):
        jstring = ''
        jstring = '{\n"header": ' + json.dumps(self.header) + ',\n' \
                  + '"mongoid": ' + json.dumps(str(self.pk)) + ',\n' \
                  + '"keyword": ' + json.dumps(self.keyword) + ',\n' \
                  + '"created": ' + json.dumps(self.created.strftime('%Y-%m-%dT%H:%M:%SZ')) + ',\n' \
                  + '"deadline": ' + json.dumps(self.deadline.strftime('%Y-%m-%dT%H:%M:%SZ')) + "}\n"

        return jstring


class Post(Document):
    text = StringField()
    user = ReferenceField(User, required=True)
    comments = ListField(StringField())
    comments_by = ListField(ReferenceField("User"))
    keyword = ListField(StringField())
    reaction = ListField(StringField())
    hilarious = ListField(ReferenceField("User"))
    well_written = ListField(ReferenceField("User"))
    amazing_story = ListField(ReferenceField("User"))

    grammar_king = ReferenceField("User")

    group = IntField()
    assignment_id = ReferenceField("Assignment")
    submit = BooleanField(default=False)

    @staticmethod
    def create(text, assignment_id):

        post = Post(text=text, user=current_user['id'], assignment_id=ObjectId(assignment_id), submit=True)
        post.save()
        return post

    @staticmethod
    def add_reaction(post_id, hilarious="", well_written="", amazing=""):

        post = Post.objects(pk=ObjectId(post_id), submit=True)
        if hilarious.lower() == 'true':
            post.update(add_to_set__hilarious=current_user['id'])
        if well_written.lower() == 'true':
            post.update(add_to_set__well_written=current_user['id'])
        if amazing.lower() == 'true':
            post.update(add_to_set__amazing_story=current_user['id'])

        return True

    @staticmethod
    def submit_assigment(text, assignment_id):

        assignment = Post.objects(user=current_user['id'], assignment_id=ObjectId(assignment_id))

        if assignment:
            assignment.update(text=text, submit=True)
            return assignment
        else:
            post = Post.create(text, assignment_id)
            post.save()
            return post

    def get_json(self):

        #print(self.user.pk)

        user_name = User.objects(pk=self.user.pk, name__exists=True)
        u_name='sample'
        if user_name:
            for u in user_name:
                u_name = u['name']

        dict_list = []
        for i in range(len(self.comments)):
            diction = {'comment': '', 'name': ''}
            diction['comment'] = self.comments[i]
            name = User.objects(pk=self.comments_by[i].pk, name__exists=True)
            another_name = ''
            if name:

                for n in name:
                    another_name = n['name']

            diction['name'] = another_name
            dict_list.append(diction)

        jstring = ''
        jstring = '{\n"text": ' + json.dumps(self.text) + ',\n' \
                  + '"name": ' + json.dumps(str(u_name)) + ',\n' \
                  + '"mongoid": ' + json.dumps(str(self.pk)) + ',\n' \
                  + '"comments": ' + json.dumps(dict_list) + ',\n' \
                  + '"hilarious": ' + json.dumps(str(len(self.hilarious))) + ',\n' \
                  + '"well_written": ' + json.dumps(str(len(self.well_written))) + ',\n' \
                  + '"amazing_story": ' + json.dumps(str(len(self.amazing_story))) + "}\n"

        return jstring

    @staticmethod
    def add_comments(post_id, comment):

        post = Post.objects(pk=ObjectId(post_id)).first()
        if(post):
            Post.objects(pk=ObjectId(post_id)).update_one(push__comments=comment, push__comments_by=current_user['id'])
            return post


def get_all_assignments():
    assignments = Assignment.objects(active=True)
    json = '{'
    json += '"success": "true","assignments":[ \n'
    for assign in assignments:
        js = assign.get_json()
        json += js + ',\n'
    json = json[:-2] + ']\n}'
    return json


def get_all_posts(assignment_id):
    already_submitted = Post.objects(assignment_id=ObjectId(assignment_id), user=current_user['id'])
    flag = False
    if already_submitted:
        flag = True

    posts = Post.objects(assignment_id=ObjectId(assignment_id), submit=True)

    jsond = '{"submitted":' + str(flag).lower() + ',\n'
    jsond += '"success": "true","posts":[ \n'

    for post in posts:
        js = post.get_json()
        jsond += js + ',\n'

    jsond = jsond[:-2] + ']\n}'
    return jsond
