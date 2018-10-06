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


@app.route('/user/<uid>', methods=['GET'])
def get_one_users(uid):

	user = User.query.filter_by(id=uid).first()

	if not user:
		return jsonify({'message': 'User not found!'})

	user_data = {}
	user_data['id'] = user.id
	user_data['name'] = user.name
	user_data['surname'] = user.surname
	user_data['email'] = user.email
	user_data['login'] = user.login
	user_data['password'] = user.password
	user_data['created'] = user.created
	user_data['updated'] = user.updated

 	return jsonify({'user': user_data})

@route_path_general.route('/user/uid', methods=['GET'])
@authenticate_jwt
def validate_user_jwt(uid):
    try:
        user = User.query.filter_by(id=uid).first()
        if not user:
            message = notFound.format("User")
            return response_with(resp.NOT_FOUND_HANDLER_404, message=message)

        return response_with(resp.SUCCESS_200)
    except Exception as e:
        logging.error(e)
        return response_with(resp.SERVER_ERROR_500)

if __name__ == '__main__':
    app.run(debug=True)