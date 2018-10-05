#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
from api.utils.database import db
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields


class Team(db.Model):
    __tablename__ = 'team'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True)
    created = db.Column(db.DateTime, server_default=db.func.now())
    updated = db.Column(db.DateTime, onupdate=db.func.now())

    def __init__(self, name):
        self.name = name

    def create(self):
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except Exception as e:
            logging.error(e)
            db.session.rollback()
            raise


class TeamSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = Team
        sqla_session = db.session

    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    created = fields.String(dump_only=True)
    updated = fields.String(dump_only=True)
