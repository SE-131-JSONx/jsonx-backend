#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import logging
from flask import Blueprint
from flask import request
from sqlalchemy.exc import IntegrityError
from api.models.user import UserSchema, User
from api.models.json import JsonSchema, Json
from api.models.json_access_map import JsonAccessMapSchema, JsonAccessMap
from api.models.team import TeamSchema, Team
from api.models.team_member_map import TeamMemberMapSchema, TeamMemberMap
from api.models.team_json_map import TeamJsonMapSchema, TeamJsonMap
from api.utils.auth import authenticate_jwt, generate_jwt, JWT
from api.utils.constants import notFound, permission, required, exists, invalid
from api.utils.enums import TeamMemberType, JsonAccessMapType
from api.utils.responses import response_with
from api.utils import responses as resp

route_path_general = Blueprint("route_path_general", __name__)


"""
USER
"""


@route_path_general.route('/v1.0/user', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        user_schema = UserSchema()
        user, error = user_schema.load(data)
        result = user_schema.dump(user.create()).data
        return response_with(resp.SUCCESS_200, value={"user": result})
    except Exception as e:
        logging.error(e)
        return response_with(resp.INVALID_INPUT_422)


@route_path_general.route('/v1.0/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        fetched = User.query.filter_by(login=data["login"]).first()

        valid_password = User.validate_password(data["password"], fetched.password if fetched else None)
        if not valid_password:
            val = {
                "message": "Invalid credentials."
            }
            return response_with(resp.BAD_REQUEST_400, value=val)

        user_schema = UserSchema()
        user, error = user_schema.dump(fetched)
        token = generate_jwt(user)
        return response_with(resp.SUCCESS_200, value={"user": user, "token": token})
    except Exception as e:
        logging.error(e)
        return response_with(resp.SERVER_ERROR_500)


@route_path_general.route('/v1.0/user/<uid>', methods=['GET'])
@authenticate_jwt
def get_user_details(uid):
    try:
        user = User.query.filter_by(id=uid).first()
        if not user:
            message = notFound.format("User")
            return response_with(resp.NOT_FOUND_HANDLER_404, message=message)

        user_schema = UserSchema()
        user_data, error = user_schema.dump(user)

        json_count = Json.count_json(uid)
        team_count = Team.count_teams(uid)

        val = {
            'id': user_data['id'],
            'name': user_data['name'],
            'surname': user_data['surname'],
            'email': user_data['email'],
            'login': user_data['login'],
            'created': user_data['created'],
            'updated': user_data['updated'],
            'json_count': json_count,
            'team_count': team_count
        }

        return response_with(resp.SUCCESS_200, value=val)
    except Exception as e:
        logging.error(e)
        return response_with(resp.SERVER_ERROR_500)


@route_path_general.route('/v1.0/user/<uid>', methods=['PUT'])
@authenticate_jwt
def update_user(uid):
    try:
        data = request.get_json()

        name = data.get("name")
        if not name:
            message = required.format("Name")
            return response_with(resp.MISSING_PARAMETERS_422, message=message)

        surname = data.get("surname")
        if not surname:
            message = required.format("Surname")
            return response_with(resp.MISSING_PARAMETERS_422, message=message)

        email = data.get("email")
        if not email:
            message = required.format("Email")
            return response_with(resp.MISSING_PARAMETERS_422, message=message)

        # validate user exists
        user = User.query.filter_by(id=uid).first()
        if not user:
            message = notFound.format("User")
            return response_with(resp.NOT_FOUND_HANDLER_404, message=message)

        # validate access to user
        access = User.query.filter_by(id=JWT.details['user_id']).first()
        if not access:
            message = permission
            return response_with(resp.NOT_FOUND_HANDLER_404, message=message)

        # update user
        user.update(name, surname, email)

        # response details
        return get_user_details(uid)
    except IntegrityError:
        message = exists.format("Name")
        return response_with(resp.INVALID_INPUT_422, message=message)
    except Exception as e:
        logging.error(e)
        return response_with(resp.SERVER_ERROR_500)


"""
JSON
"""


@route_path_general.route('/v1.0/json/save', methods=['POST'])
@authenticate_jwt
def save_json():

    try:
        data = request.get_json()

        # validate json syntax
        json.loads(data['data'])

        # save json in json table
        json_schema = JsonSchema()
        _json, error = json_schema.load(data)
        result = json_schema.dump(_json.create()).data

        # save an entry in json_access_map
        json_access_schema = JsonAccessMapSchema()
        json_access_data = {
            "user": JWT.details['user_id'],
            "json": result['id'],
            "_type": JsonAccessMapType.OWNER.value
        }
        json_access, error = json_access_schema.load(json_access_data)
        json_access.create()

        val = {
            "id": result['id'],
            "message": "Success"
        }

        return response_with(resp.SUCCESS_200, value=val)
    except ValueError as e:
        logging.error(e)

        msg = invalid.format("JSON")
        return response_with(resp.INVALID_INPUT_422, message=msg)
    except Exception as e:
        logging.error(e)
        return response_with(resp.SERVER_ERROR_500)


@route_path_general.route('/v1.0/json/<json_id>', methods=['GET'])
@authenticate_jwt
def get_json(json_id):
    try:
        # validate json exists
        json = Json.query.filter_by(id=json_id).first()
        if not json:
            message = notFound.format("JSON")
            return response_with(resp.NOT_FOUND_HANDLER_404, message=message)

        # validate access to json
        access = JsonAccessMap.query.filter_by(json=json_id, user=JWT.details['user_id']).first()
        if not access:
            message = permission
            return response_with(resp.NOT_FOUND_HANDLER_404, message=message)

        # response details
        access_schema = JsonAccessMapSchema()
        json_access_data, error = access_schema.dump(access)
        json_schema = JsonSchema()
        json_data, error = json_schema.dump(json)

        val = {
            'id': json_data['id'],
            'data': json_data['data'],
            'permission': json_access_data['type'],
            'created': json_data['created'],
            'updated': json_data['updated']
        }

        return response_with(resp.SUCCESS_200, value=val)
    except Exception as e:
        logging.error(e)
        return response_with(resp.SERVER_ERROR_500)


@route_path_general.route('/v1.0/json/<json_id>/team/<team_id>', methods=['POST'])
@authenticate_jwt
def give_team_json_access(json_id, team_id):
    try:
        # validate json exists
        json = Json.query.filter_by(id=json_id).first()
        if not json:
            message = notFound.format("JSON")
            return response_with(resp.NOT_FOUND_HANDLER_404, message=message)

        # validate team exists
        team = Team.query.filter_by(id=team_id).first()
        if not team:
            message = notFound.format("Team")
            return response_with(resp.NOT_FOUND_HANDLER_404, message=message)

        # validate access to json
        access = JsonAccessMap.query\
            .filter_by(json=json_id, user=JWT.details['user_id'], type=JsonAccessMapType.OWNER.value)\
            .first()
        if not access:
            message = permission
            return response_with(resp.NOT_FOUND_HANDLER_404, message=message)

        # if user does not have access, grant access
        access_already_exists = TeamJsonMap.query.filter_by(team=team_id, json=json_id).first()
        if not access_already_exists:
            # add access
            team_access_data = {
                "team": team_id,
                "json": json_id,
            }

            team_json_json_map = TeamJsonMapSchema()
            team_json, error = team_json_json_map.load(team_access_data)
            team_json.create()

        val = {
            "team": team_id,
            "json": json_id
        }

        return response_with(resp.SUCCESS_200, value=val)
    except Exception as e:
        logging.error(e)
        return response_with(resp.SERVER_ERROR_500)


@route_path_general.route('/v1.0/json/<json_id>/team/<team_id>', methods=['DELETE'])
@authenticate_jwt
def remove_team_json_access(json_id, team_id):
    try:
        # validate json exists
        json = Json.query.filter_by(id=json_id).first()
        if not json:
            message = notFound.format("JSON")
            return response_with(resp.NOT_FOUND_HANDLER_404, message=message)

        # validate team exists
        team = Team.query.filter_by(id=team_id).first()
        if not team:
            message = notFound.format("Team")
            return response_with(resp.NOT_FOUND_HANDLER_404, message=message)

        # validate access to json
        access = JsonAccessMap.query\
            .filter_by(json=json_id, user=JWT.details['user_id'], type=TeamMemberType.OWNER.value)\
            .first()
        if not access:
            message = permission
            return response_with(resp.NOT_FOUND_HANDLER_404, message=message)

        # if team has access, remove access
        json_access = TeamJsonMap.query.filter_by(team=team_id, json=json_id).first()
        if json_access:
            json_access.delete()

        return response_with(resp.SUCCESS_200)
    except Exception as e:
        logging.error(e)
        return response_with(resp.SERVER_ERROR_500)


"""
TEAM
"""


@route_path_general.route('/v1.0/team', methods=['POST'])
@authenticate_jwt
def create_team():
    try:
        data = request.get_json()
        team_schema = TeamSchema()
        team, error = team_schema.load(data)
        result = team_schema.dump(team.create()).data

        team_member_data = {
            "user": JWT.details['user_id'],
            "team": result['id'],
            "_type": TeamMemberType.OWNER.value
        }

        team_member_map = TeamMemberMapSchema()
        team_member, error = team_member_map.load(team_member_data)
        team_member.create()

        return response_with(resp.SUCCESS_200, value={"team": result})
    except IntegrityError:
        message = exists.format("Name")
        return response_with(resp.INVALID_INPUT_422, message=message)
    except Exception as e:
        logging.error(e)
        return response_with(resp.INVALID_INPUT_422)


@route_path_general.route('/v1.0/team/<team_id>', methods=['GET'])
@authenticate_jwt
def get_team(team_id):
    try:
        # validate team exists
        team = Team.query.filter_by(id=team_id).first()
        if not team:
            message = notFound.format("Team")
            return response_with(resp.NOT_FOUND_HANDLER_404, message=message)

        # validate access to team
        access = TeamMemberMap.query.filter_by(team=team_id, user=JWT.details['user_id']).first()
        if not access:
            message = permission
            return response_with(resp.NOT_FOUND_HANDLER_404, message=message)

        # response details
        team_schema = TeamSchema()
        team_data, error = team_schema.dump(team)
        team_member_schema = TeamMemberMapSchema()
        team_member_data, error = team_member_schema.dump(access)

        val = {
            'id': team_data['id'],
            'name': team_data['name'],
            'type': team_member_data['type'],
            'created': team_data['created'],
            'updated': team_data['updated']
        }

        return response_with(resp.SUCCESS_200, value=val)
    except Exception as e:
        logging.error(e)
        return response_with(resp.SERVER_ERROR_500)


@route_path_general.route('/v1.0/team/<team_id>', methods=['PUT'])
@authenticate_jwt
def update_team(team_id):
    try:
        data = request.get_json()

        name = data.get("name")
        if not name:
            message = required.format("Name")
            return response_with(resp.MISSING_PARAMETERS_422, message=message)

        # validate team exists
        team = Team.query.filter_by(id=team_id).first()
        if not team:
            message = notFound.format("Team")
            return response_with(resp.NOT_FOUND_HANDLER_404, message=message)

        # validate access to team
        access = TeamMemberMap.query.filter_by(team=team_id, user=JWT.details['user_id']).first()
        if not access:
            message = permission
            return response_with(resp.NOT_FOUND_HANDLER_404, message=message)

        # update team
        team.update(name)

        # response details
        team_schema = TeamSchema()
        team_data, error = team_schema.dump(team)

        return response_with(resp.SUCCESS_200, value={"team": team_data})
    except IntegrityError:
        message = exists.format("Name")
        return response_with(resp.INVALID_INPUT_422, message=message)
    except Exception as e:
        logging.error(e)
        return response_with(resp.SERVER_ERROR_500)


@route_path_general.route('/v1.0/team/<team_id>', methods=['DELETE'])
@authenticate_jwt
def delete_team(team_id):
    try:
        # validate team exists
        team = Team.query.filter_by(id=team_id).first()
        if not team:
            message = notFound.format("Team")
            return response_with(resp.NOT_FOUND_HANDLER_404, message=message)

        # validate access to team
        access = TeamMemberMap.query\
            .filter_by(team=team_id, user=JWT.details['user_id'], type=TeamMemberType.OWNER.value)\
            .first()
        if not access:
            message = permission
            return response_with(resp.NOT_FOUND_HANDLER_404, message=message)

        # delete team
        team.delete()

        return response_with(resp.SUCCESS_200)
    except Exception as e:
        logging.error(e)
        return response_with(resp.SERVER_ERROR_500)


@route_path_general.route('/v1.0/team/<team_id>/access', methods=['POST'])
@authenticate_jwt
def add_team_member(team_id):
    try:
        data = request.get_json()

        # require user
        user = data.get("user")
        if not user:
            message = required.format("User")
            return response_with(resp.MISSING_PARAMETERS_422, message=message)

        # validate team exists
        team = Team.query.filter_by(id=team_id).first()
        if not team:
            message = notFound.format("Team")
            return response_with(resp.NOT_FOUND_HANDLER_404, message=message)

        # validate user exists
        user_exists = User.query.filter_by(id=user).first()
        if not user_exists:
            message = notFound.format("User")
            return response_with(resp.NOT_FOUND_HANDLER_404, message=message)

        # validate access to team
        access = TeamMemberMap.query\
            .filter_by(team=team_id, user=JWT.details['user_id'], type=TeamMemberType.OWNER.value)\
            .first()
        if not access:
            message = permission
            return response_with(resp.NOT_FOUND_HANDLER_404, message=message)

        # if user does not have access, grant access
        access_already_exists = TeamMemberMap.query.filter_by(team=team_id, user=user).first()
        if not access_already_exists:
            # add access
            team_member_data = {
                "user": user,
                "team": team_id,
                "_type": TeamMemberType.MEMBER.value
            }

            team_member_map = TeamMemberMapSchema()
            team_member, error = team_member_map.load(team_member_data)
            team_member.create()

        return response_with(resp.SUCCESS_200)
    except Exception as e:
        logging.error(e)
        return response_with(resp.SERVER_ERROR_500)


@route_path_general.route('/v1.0/team/<team_id>/access/<user_id>', methods=['DELETE'])
@authenticate_jwt
def remove_team_member(team_id, user_id):
    try:
        # validate team exists
        team = Team.query.filter_by(id=team_id).first()
        if not team:
            message = notFound.format("Team")
            return response_with(resp.NOT_FOUND_HANDLER_404, message=message)

        # validate user exists
        user_exists = User.query.filter_by(id=user_id).first()
        if not user_exists:
            message = notFound.format("User")
            return response_with(resp.NOT_FOUND_HANDLER_404, message=message)

        # validate access to team
        access = TeamMemberMap.query\
            .filter_by(team=team_id, user=JWT.details['user_id'], type=TeamMemberType.OWNER.value) \
            .first()
        if not access:
            message = permission
            return response_with(resp.NOT_FOUND_HANDLER_404, message=message)

        # if team member exists, delete
        team_member = TeamMemberMap.query.filter_by(team=team_id, user=user_id).first()
        if team_member:
            team_member.delete()

        return response_with(resp.SUCCESS_200)
    except Exception as e:
        logging.error(e)
        return response_with(resp.SERVER_ERROR_500)
