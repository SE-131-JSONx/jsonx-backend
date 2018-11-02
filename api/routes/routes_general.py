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
from api.utils.validation import validate_teams, validate_users

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

        json_count = Json.count_accessible_json(uid)
        owned_json_count = Json.count_owned_json(uid)
        shared_json_count = Json.count_shared_json(uid)
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
            'team_count': team_count,
            'owned_json_count': owned_json_count,
            'shared_json_count': shared_json_count
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


@route_path_general.route('/v1.0/user', methods=['GET'])
@authenticate_jwt
def search_user():
    try:
        q = request.args.get('q')
        user = User.search(q)

        user_schema = UserSchema()

        values = {
            "user": []
        }
        for u in user:
            user_data = user_schema.dump(u)[0]
            values['user'].append({
                'id': user_data['id'],
                'name': user_data['name'],
                'surname': user_data['surname'],
                'email': user_data['email'],
                'login': user_data['login'],
                'created': user_data['created'],
                'updated': user_data['updated']
            })
        return response_with(resp.SUCCESS_200, value=values)
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
        json_, error = json_schema.load(data)
        result = json_schema.dump(json_.create()).data

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
        json_ = Json.query.filter_by(id=json_id).first()
        if not json_:
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
            'title': json_data['title'],
            'data': json_data['data'],
            'permission': json_access_data['type'],
            'created': json_data['created'],
            'updated': json_data['updated']
        }

        return response_with(resp.SUCCESS_200, value=val)
    except Exception as e:
        logging.error(e)
        return response_with(resp.SERVER_ERROR_500)


@route_path_general.route('/v1.0/json/<jid>', methods=['PUT'])
@authenticate_jwt
def update_json(jid):
    try:
        data = request.get_json()

        title = data.get("title")
        if not title:
            message = required.format("Title")
            return response_with(resp.MISSING_PARAMETERS_422, message=message)

        _data = data.get("data")
        if not _data:
            message = required.format("Data")
            return response_with(resp.MISSING_PARAMETERS_422, message=message)

        # validate user exists
        json_ = Json.query.filter_by(id=jid).first()
        if not json_:
            message = notFound.format("JSON")
            return response_with(resp.NOT_FOUND_HANDLER_404, message=message)

        # validate access to json
        access = JsonAccessMap.query.filter_by(user=JWT.details['user_id'], json=jid).first()
        if not access:
            message = permission
            return response_with(resp.NOT_FOUND_HANDLER_404, message=message)

        # update json
        json_.update(title, _data)

        # response details
        return get_json(jid)
    except IntegrityError:
        message = exists.format("Title")
        return response_with(resp.INVALID_INPUT_422, message=message)
    except Exception as e:
        logging.error(e)
        return response_with(resp.SERVER_ERROR_500)


@route_path_general.route('/v1.0/json', methods=['GET'])
@authenticate_jwt
def search_json():
    try:
        q = request.args.get('q')
        json_ = Json.search(JWT.details['user_id'], q)

        json_schema = JsonSchema()

        values = {
            "json": [json_schema.dump(j)[0] for j in json_]
        }

        return response_with(resp.SUCCESS_200, value=values)
    except Exception as e:
        logging.error(e)
        return response_with(resp.SERVER_ERROR_500)


@route_path_general.route('/v1.0/json/<jid>/group', methods=['GET'])
@authenticate_jwt
def search_json_access_users(jid):
    try:
        q = request.args.get('q')

        # validate json exists
        _json = Json.query.filter_by(id=jid).first()
        if not _json:
            message = notFound.format("Json")
            return response_with(resp.NOT_FOUND_HANDLER_404, message=message)

        # validate access to team
        teams = TeamMemberMap.query.filter_by(user=JWT.details['user_id']).all()
        access_by_team = None
        for team in teams:
            access_by_team = TeamJsonMap.query.filter_by(json=jid, team=team.id).first() \
                if TeamJsonMap.query.filter_by(json=jid, team=team.id).first() else access_by_team

        access_by_user = JsonAccessMap.query.filter_by(json=jid, user=JWT.details['user_id']).first()
        if not access_by_team and not access_by_user:
            message = permission
            return response_with(resp.NOT_FOUND_HANDLER_404, message=message)

        users = Json.search_members(q, jid)

        user_schema = UserSchema()

        values = {
            "user": []
        }
        for u in users:
            user_data = user_schema.dump(u)[0]
            values['user'].append({
                'id': user_data['id'],
                'name': user_data['name'],
                'surname': user_data['surname'],
                'email': user_data['email'],
                'login': user_data['login'],
                'created': user_data['created'],
                'updated': user_data['updated']
            })

        return response_with(resp.SUCCESS_200, value=values)
    except Exception as e:
        logging.error(e)
        return response_with(resp.SERVER_ERROR_500)


@route_path_general.route('/v1.0/json/<json_id>', methods=['DELETE'])
@authenticate_jwt
def delete_json(json_id):
    try:
        # validate json exists
        _json = Json.query.filter_by(id=json_id).first()
        if not _json:
            message = notFound.format("JSON")
            return response_with(resp.NOT_FOUND_HANDLER_404, message=message)

        # validate access to json
        access = JsonAccessMap.query\
            .filter_by(json=json_id, user=JWT.details['user_id'], type=JsonAccessMapType.OWNER.value)\
            .first()
        if not access:
            message = permission
            return response_with(resp.NOT_FOUND_HANDLER_404, message=message)

        # delete json
        _json.delete()

        return response_with(resp.SUCCESS_200)
    except Exception as e:
        logging.error(e)
        return response_with(resp.SERVER_ERROR_500)


@route_path_general.route('/v1.0/json/<json_id>/team/<team_id>', methods=['POST'])
@authenticate_jwt
def give_team_json_access(json_id, team_id):
    try:
        # validate json exists
        json_ = Json.query.filter_by(id=json_id).first()
        if not json_:
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

        # if team does not have access, grant access
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
        json_ = Json.query.filter_by(id=json_id).first()
        if not json_:
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


@route_path_general.route('/v1.0/json/<jid>/group', methods=['DELETE'])
@authenticate_jwt
def remove_group(jid):
    try:
        data = request.get_json()
        users = data.get('users', [])
        teams = data.get('teams', [])

        if not users and not teams:
            message = required.format("Users or teams")
            return response_with(resp.MISSING_PARAMETERS_422, message=message)

        # validate json exists
        _json = Json.query.filter_by(id=jid).first()
        if not _json:
            message = notFound.format("JSON")
            return response_with(resp.NOT_FOUND_HANDLER_404, message=message)

        invalid_users = validate_users(users)
        if invalid_users:
            return invalid_users

        invalid_teams = validate_teams(teams)
        if invalid_teams:
            return invalid_teams

        # if user json map exists, delete
        for user in users:
            user_json_map = JsonAccessMap.query.filter_by(json=jid, user=user).first()
            if user_json_map:
                user_json_map.delete()

        # if team json map exists, delete
        for team in teams:
            team_json_map = TeamJsonMap.query.filter_by(json=jid, team=team).first()
            if team_json_map:
                team_json_map.delete()

        return response_with(resp.SUCCESS_200)
    except Exception as e:
        logging.error(e)
        return response_with(resp.SERVER_ERROR_500)


@route_path_general.route('/v1.0/json/<jid>/group', methods=['POST'])
@authenticate_jwt
def add_group(jid):
    try:
        data = request.get_json()
        users = data.get('users', [])
        teams = data.get('teams', [])

        if not users and not teams:
            message = required.format("Users or teams")
            return response_with(resp.MISSING_PARAMETERS_422, message=message)

        # validate json exists
        _json = Json.query.filter_by(id=jid).first()
        if not _json:
            message = notFound.format("JSON")
            return response_with(resp.NOT_FOUND_HANDLER_404, message=message)

        invalid_users = validate_users(users)
        if invalid_users:
            return invalid_users

        invalid_teams = validate_teams(teams)
        if invalid_teams:
            return invalid_teams

        # if user json map does not exist, create
        for user in users:
            # if user does not have access, grant access
            access_already_exists = JsonAccessMap.query.filter_by(user=user, json=jid).first()
            if not access_already_exists:
                # add access
                json_access_data = {
                    "user": user,
                    "json": jid,
                    "_type": 1
                }

                json_access_map = JsonAccessMapSchema()
                user_json, error = json_access_map.load(json_access_data)
                user_json.create()

        for team in teams:
            # if team does not have access, grant access
            access_already_exists = TeamJsonMap.query.filter_by(team=team, json=jid).first()
            if not access_already_exists:
                # add access
                team_access_data = {
                    "team": team,
                    "json": jid,
                }

                team_json_map = TeamJsonMapSchema()
                team_json, error = team_json_map.load(team_access_data)
                team_json.create()

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


@route_path_general.route('/v1.0/team', methods=['GET'])
@authenticate_jwt
def search_team():
    try:
        q = request.args.get('q')
        team = Team.search(JWT.details['user_id'], q)

        team_schema = TeamSchema()

        values = {
            "team": [team_schema.dump(t)[0] for t in team]
        }

        for team in values["team"]:
            team["members"], team["access_level"] = TeamMemberMap.search_detail(team['id'], JWT.details['user_id'])

        return response_with(resp.SUCCESS_200, value=values)
    except Exception as e:
        logging.error(e)
        return response_with(resp.SERVER_ERROR_500)


@route_path_general.route('/v1.0/team/<tid>/members', methods=['GET'])
@authenticate_jwt
def search_team_members(tid):
    try:
        q = request.args.get('q')

        # validate team exists
        team = Team.query.filter_by(id=tid).first()
        if not team:
            message = notFound.format("Team")
            return response_with(resp.NOT_FOUND_HANDLER_404, message=message)

        # validate access to team
        access = TeamMemberMap.query.filter_by(team=tid, user=JWT.details['user_id']).first()
        if not access:
            message = permission
            return response_with(resp.NOT_FOUND_HANDLER_404, message=message)

        users = Team.search_members(q, tid)

        user_schema = UserSchema()

        values = {
            "user": []
        }
        for u in users:
            user_data = user_schema.dump(u)[0]
            values['user'].append({
                'id': user_data['id'],
                'name': user_data['name'],
                'surname': user_data['surname'],
                'email': user_data['email'],
                'login': user_data['login'],
                'created': user_data['created'],
                'updated': user_data['updated']
            })

        return response_with(resp.SUCCESS_200, value=values)
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
        users = data.get("users")
        if not users:
            message = required.format("Users")
            return response_with(resp.MISSING_PARAMETERS_422, message=message)

        # validate team exists
        team = Team.query.filter_by(id=team_id).first()
        if not team:
            message = notFound.format("Team")
            return response_with(resp.NOT_FOUND_HANDLER_404, message=message)

        # validate user exists
        for user in users:
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
        for user in users:
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


@route_path_general.route('/v1.0/team/<team_id>/access', methods=['DELETE'])
@authenticate_jwt
def remove_team_member(team_id):
    try:
        data = request.get_json()

        # validate team exists
        team = Team.query.filter_by(id=team_id).first()
        if not team:
            message = notFound.format("Team")
            return response_with(resp.NOT_FOUND_HANDLER_404, message=message)

        for user in data.get('users'):
            # validate user exists
            user_exists = User.query.filter_by(id=user).first()
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
        for user in data.get('users'):
            team_member = TeamMemberMap.query.filter_by(team=team_id, user=user).first()
            if team_member:
                team_member.delete()

        return response_with(resp.SUCCESS_200)
    except Exception as e:
        logging.error(e)
        return response_with(resp.SERVER_ERROR_500)
