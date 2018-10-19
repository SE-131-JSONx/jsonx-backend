#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
from sqlalchemy import or_
from sqlalchemy.sql.functions import count
from api.models.json_access_map import JsonAccessMap
from api.models.team import Team
from api.models.team_json_map import TeamJsonMap
from api.models.team_member_map import TeamMemberMap
from api.utils.database import db
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields


class Json(db.Model):
    __tablename__ = 'json'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255))
    data = db.Column(db.String(10000))
    created = db.Column(db.DateTime, server_default=db.func.now())
    updated = db.Column(db.DateTime, onupdate=db.func.now())

    def __init__(self, data, title):
        self.data = data
        self.title = title

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    @staticmethod
    def count_json(uid):
        """Count the number of JSONs a user has access to
        :param uid:
        :return: int
        """
        try:
            # get json through user mapping path
            query_user_json = db.session.query(Json.id).join(JsonAccessMap).filter(JsonAccessMap.user == uid)

            # get json through team mapping path
            teams = db.session.query(Team.id).join(TeamMemberMap).filter(TeamMemberMap.user == uid)
            query_team_json = db.session.query(Json.id).join(TeamJsonMap).filter(TeamJsonMap.team.in_(teams))

            # count distinct json in team and user path
            json_count = db.session.query(count(Json.id.distinct()))\
                .filter(or_(Json.id.in_(query_user_json),
                            Json.id.in_(query_team_json))).scalar()
            return json_count
        except Exception as e:
            logging.error(e)
            raise

    @staticmethod
    def search(uid, q):
        """Fitlers and returns JSONs by uid and search query
        :param uid:
        :param q: search query
        :return: int
        """
        try:
            # get json through user mapping path
            query_user_json = db.session.query(Json.id).join(JsonAccessMap).filter(JsonAccessMap.user == uid)

            # get json through team mapping path
            teams = db.session.query(Team.id).join(TeamMemberMap).filter(TeamMemberMap.user == uid)
            query_team_json = db.session.query(Json.id).join(TeamJsonMap).filter(TeamJsonMap.team.in_(teams))

            # count distinct json in team and user path
            _json = db.session.query(Json) \
                .filter(or_(Json.id.in_(query_user_json),
                            Json.id.in_(query_team_json)))
            if q is not None:
                _json = _json.filter(or_(Json.title.like('%{}%'.format(q)),
                                     Json.data.like('%{}%'.format(q))))
            return _json.all()
        except Exception as e:
            logging.error(e)
            raise


class JsonSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = Json
        sqla_session = db.session

    id = fields.Integer(dump_only=True)
    title = fields.String(required=True)
    data = fields.String(required=True)
    created = fields.String(dump_only=True)
    updated = fields.String(dump_only=True)
