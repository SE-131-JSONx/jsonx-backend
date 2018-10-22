#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
from sqlalchemy import or_
from api.utils.auth import JWT
from api.utils.database import db
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields
import bcrypt


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255))
    surname = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    login = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    created = db.Column(db.DateTime, server_default=db.func.now())
    updated = db.Column(db.DateTime, onupdate=db.func.now())

    def __init__(self, name, surname, email, login, password):
        self.name = name
        self.surname = surname
        self.email = email
        self.login = login
        self.password = self._hash(password)

    def create(self):
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except Exception as e:
            logging.error(e)
            db.session.rollback()
            raise

    def update(self, name, surname, email):
        try:
            commit = False
            if name != self.name:
                self.name = name
                commit = True
            if surname != self.surname:
                self.surname = surname
                commit = True
            if email != self.email:
                self.email = email
                commit = True
            if commit:
                db.session.commit()
        except Exception as e:
            logging.error(e)
            db.session.rollback()
            raise

    @staticmethod
    def search(q):
        """Filters and returns users by search query
        :param q: search query
        :return: User
        """
        try:
            # get json through user mapping path
            user = db.session.query(User).filter(User.id != JWT.details['user_id'])

            if q is not None:
                user = user.filter(or_(User.name.like('%{}%'.format(q)),
                                       User.surname.like('%{}%'.format(q)),
                                       User.email.like('%{}%'.format(q)),
                                       User.login.like('%{}%'.format(q))))
            return user.limit(50).all()
        except Exception as e:
            logging.error(e)
            raise

    @staticmethod
    def _hash(password):
        """Hashes the password
        :param password:
        :return:
        """
        return bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

    @classmethod
    def validate_password(cls, password, hashed):
        """Validate that the password hashes to the hashed value.
        :param hashed:
        :param password:
        :return:
        """
        return \
            password \
            and hashed \
            and bcrypt.hashpw(password.encode('utf8'), hashed.encode('utf8')) == hashed.encode('utf8')


class UserSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = User
        sqla_session = db.session

    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    surname = fields.String(required=True)
    email = fields.String(required=True)
    login = fields.String(required=True)
    password = fields.String(required=True)
    created = fields.String(dump_only=True)
    updated = fields.String(dump_only=True)
