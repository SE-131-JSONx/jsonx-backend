#!/usr/bin/python
# -*- coding: utf-8 -*-

from api.models.json import Json, JsonSchema
from api.models.team import Team
from api.models.team_member_map import TeamMemberMap
from api.models.user import User
from api.utils.database import db
from faker import Faker

fake = Faker()


def create_users(num=1):
    users = [{
        "name": fake.first_name(),
        "surname": fake.last_name(),
        "email": fake.ascii_company_email(),
        "login": fake.user_name(),
        "password": fake.bban()
    } for _ in range(0, num)]
    for user in users:
        User(name=user["name"],
             surname=user["surname"],
             email=user["email"],
             login=user["login"],
             password=user["password"]).create()
    return users


def delete_users(users):
    db.session.query(User).filter(User.login.in_([user["login"] for user in users])).delete(synchronize_session=False)
    db.session.commit()


def create_json():
    _json = [{
        'data': fake.first_name()
    }]
    for j in _json:
        Json(data=j['data']).create()
        j.update(get_json_id(j['data']))
    return _json


def get_json_id(data):
    json_schema = JsonSchema()
    _json = Json.query.filter_by(data=data).first()
    json_data, error = json_schema.dump(_json)
    val = {
        'id': json_data['id'],
        'data': json_data['data'],
        'created': json_data['created'],
        'updated': json_data['updated']
    }
    return val


def delete_json(_json):
    db.session.query(Json).filter(Json.id.in_([j['id'] for j in _json])).delete(synchronize_session=False)
    db.session.commit()


def delete_teams(teams):
    db.session.query(Team).filter(Team.id.in_([team for team in teams])).delete(synchronize_session=False)


def delete_team_members(users):
    users = db.session.query(User.id).filter(User.login.in_([user["login"] for user in users]))

    db.session.query(TeamMemberMap).filter(TeamMemberMap.user.in_(users)).delete(synchronize_session=False)
    db.session.commit()
