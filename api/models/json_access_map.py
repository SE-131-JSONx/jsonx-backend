#!/usr/bin/python
# -*- coding: utf-8 -*-

from sqlalchemy import ForeignKey
from api.utils.database import db
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields


class JsonAccessMap(db.Model):
    __tablename__ = 'json_access_map'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user = db.Column(db.BigInteger, ForeignKey("user.id"))
    json = db.Column(db.BigInteger, ForeignKey("json.id"))
    type = db.Column(db.Integer)
    created = db.Column(db.DateTime, server_default=db.func.now())
    updated = db.Column(db.DateTime, onupdate=db.func.now())

    def __init__(self, user, json, _type):
        self.user = user
        self.json = json
        self.type = _type

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self


class JsonAccessMapSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = JsonAccessMap
        sqla_session = db.session

    id = fields.Integer(dump_only=True)
    user = fields.Integer(required=True)
    json = fields.Integer(required=True)
    type = fields.Integer(required=True)
    created = fields.String(dump_only=True)
    updated = fields.String(dump_only=True)
