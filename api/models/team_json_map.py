#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging

from sqlalchemy import ForeignKey
from api.utils.database import db
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields


class TeamJsonMap(db.Model):
    __tablename__ = 'team_json_map'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    team = db.Column(db.BigInteger, ForeignKey("team.id"))
    json = db.Column(db.BigInteger, ForeignKey("json.id"))
    created = db.Column(db.DateTime, server_default=db.func.now())
    updated = db.Column(db.DateTime, onupdate=db.func.now())

    def __init__(self, team, json):
        self.team = team
        self.json = json

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            logging.error(e)
            raise


class TeamJsonMapSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = TeamJsonMap
        sqla_session = db.session

    id = fields.Integer(dump_only=True)
    team = fields.Integer(required=True)
    json = fields.Integer(required=True)
    created = fields.String(dump_only=True)
    updated = fields.String(dump_only=True)
