#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
from sqlalchemy import ForeignKey
from sqlalchemy.sql.functions import count
from api.utils.database import db
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields


class TeamMemberMap(db.Model):
    __tablename__ = 'team_member_map'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user = db.Column(db.BigInteger, ForeignKey("user.id"))
    team = db.Column(db.BigInteger, ForeignKey("team.id"))
    type = db.Column(db.Integer)
    created = db.Column(db.DateTime, server_default=db.func.now())
    updated = db.Column(db.DateTime, onupdate=db.func.now())

    def __init__(self, user, team, _type):
        self.user = user
        self.team = team
        self.type = _type

    def create(self):
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except Exception as e:
            logging.error(e)
            db.session.rollback()
            raise

    @staticmethod
    def count_members(tid):
        """Count the number of members in a team
        :param tid:
        :return: int
        """
        try:
            # get json through user mapping path
            query_member_json = db.session.query(count(TeamMemberMap.id)).filter(TeamMemberMap.team == tid).scalar()
            return query_member_json
        except Exception as e:
            logging.error(e)
            raise

    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            logging.error(e)
            raise


class TeamMemberMapSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = TeamMemberMap
        sqla_session = db.session

    id = fields.Integer(dump_only=True)
    user = fields.Integer(required=True)
    team = fields.Integer(required=True)
    _type = fields.Integer(required=True)
    created = fields.String(dump_only=True)
    updated = fields.String(dump_only=True)
