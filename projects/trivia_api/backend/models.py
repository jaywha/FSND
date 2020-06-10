import os
from sqlalchemy import Column, String, Integer, create_engine
from flask_sqlalchemy import SQLAlchemy
import json
import base64

database_user = "jayw6"
database_pass = base64.b64decode('anVzdDRtZQ=='.encode('ascii')).decode('ascii')
database_URLPort = 'localhost:5432'
database_name = "trivia"
database_path = "postgres://{}:{}@{}/{}".format(database_user, database_pass, database_URLPort, database_name)

db = SQLAlchemy()


def setup_db(app, db_path=database_path):
    """
    Binds a flask application and a SQLAlchemy service
    """
    app.config["SQLALCHEMY_DATABASE_URI"] = db_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()
    fix_category_index_error()
    return db


def fix_category_index_error():
    placeholder = Category.query.filter_by(id=0).first()
    if not placeholder:
        dummy_cat = Category("PLACEHOLDER")
        dummy_cat.id = 0
        db.session.add(dummy_cat)
        db.session.commit()


'''
Question

'''


class Question(db.Model):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True)
    question = Column(String)
    answer = Column(String)
    category = Column(String)
    difficulty = Column(Integer)

    def __init__(self, question, answer, category, difficulty):
        self.question = question
        self.answer = answer
        self.category = category
        self.difficulty = difficulty

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'question': self.question,
            'answer': self.answer,
            'category': self.category,
            'difficulty': self.difficulty
        }


'''
Category

'''


class Category(db.Model):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    type = Column(String)

    def __init__(self, type):
        self.type = type

    def format(self):
        return {
            'id': self.id,
            'type': self.type
        }


'''
User

'''


class User(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    scores = Column(String)

    def __init__(self, type):
        self.type = type

    def format(self):
        return {
            'id': self.id,
            'type': self.type,
            'scores': self.scores
        }

