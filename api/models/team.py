#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
from sqlalchemy.sql.functions import count
from api.models.team_member_map import TeamMemberMap
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

    def update(self, name):
        try:
            if name != self.name:
                self.name = name
                db.session.commit()
        except Exception as e:
            logging.error(e)
            db.session.rollback()
            raise

    @staticmethod
    def search(uid, q):
        """Fitlers and returns Teams by uid and search query
        :param uid:
        :param q: search query
        :return: int
        """
        try:
            # get team through team mapping path
            query_team = db.session.query(Team.id).join(TeamMemberMap).filter(TeamMemberMap.user == uid)

            team = db.session.query(Team) \
                .filter(Team.id.in_(query_team))
            if q is not None:
                team = team.filter(Team.name.like('%{}%'.format(q)))
            return team.all()
        except Exception as e:
            logging.error(e)
            raise

    def delete(self):
        try:
            db.session.query(TeamMemberMap).filter(TeamMemberMap.team == self.id).delete()
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            logging.error(e)
            db.session.rollback()
            raise

    @staticmethod
    def count_teams(uid):
        """Counts the number of teams a user has access to
        :param uid:
        :return: int
        """
        try:
            team_count = db.session.query(count(Team.id))\
                .join(TeamMemberMap).filter(TeamMemberMap.user == uid).scalar()
            return team_count
        except Exception as e:
            logging.error(e)
            raise


class TeamSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = Team
        sqla_session = db.session

    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    created = fields.String(dump_only=True)
    updated = fields.String(dump_only=True)
