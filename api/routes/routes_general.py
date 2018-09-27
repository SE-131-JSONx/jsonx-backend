#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Blueprint
from flask import request
from api.models.user import UserSchema, User
from api.models.json import JsonSchema, Json
from api.models.json_access_map import JsonAccessMapSchema, JsonAccessMap
from api.utils.auth import authenticate_jwt, generate_jwt
from api.utils.responses import response_with
from api.utils import responses as resp

route_path_general = Blueprint("route_path_general", __name__)


@route_path_general.route('/v1.0/user', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        user_schema = UserSchema()
        user, error = user_schema.load(data)
        result = user_schema.dump(user.create()).data
        return response_with(resp.SUCCESS_200, value={"user": result})
    except Exception as e:
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
        return response_with(resp.SERVER_ERROR_500)
