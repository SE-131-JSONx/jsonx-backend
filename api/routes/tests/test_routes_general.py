#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
from api.routes.tests.utils.db_operation import create_users, create_json, delete_users, delete_json
from api.utils.constants import notFound, permission
from api.utils.test_base import BaseTestCase
from faker import Faker

fake = Faker()


class TestUser(BaseTestCase):
    users = None

    def setUp(self):
        super(TestUser, self).setUp()
        self.users = create_users()

    def tearDown(self):
        delete_users(self.users)

    def test_create_user(self):
        user = {
            "name": fake.first_name(),
            "surname": fake.last_name(),
            "email": fake.ascii_company_email(),
            "login": fake.user_name(),
            "password": fake.bban()
        }
        response = self.app.post(
            "/api/v1.0/user",
            data=json.dumps(user),
            content_type="application/json",
        )
        data = json.loads(response.data)
        self.assertEqual(200, response.status_code)
        self.assertTrue("user" in data)
        self.users.append(user)

    def test_login_invalid(self):
        login = {
            "login": "invalid_username",
            "password": "invalid_password"
        }
        response = self.app.post(
            "/api/v1.0/login",
            data=json.dumps(login),
            content_type="application/json",
        )
        data = json.loads(response.data)
        self.assertEqual(400, response.status_code)
        self.assertTrue("message" in data)

    def test_login_valid(self):
        login = {
            "login": self.users[0]["login"],
            "password": self.users[0]["password"]
        }
        response = self.app.post(
            "/api/v1.0/login",
            data=json.dumps(login),
            content_type="application/json",
        )
        data = json.loads(response.data)
        self.assertEqual(200, response.status_code)
        self.assertTrue("user" in data)


class TestJson(BaseTestCase):
    users = None
    _json = None

    def setUp(self):
        super(TestJson, self).setUp()
        self.users = create_users()
        self._json = create_json()

    def tearDown(self):
        delete_users(self.users)
        delete_json(self._json)

    def test_json_not_found(self):
        login = {
            "login": self.users[0]["login"],
            "password": self.users[0]["password"]
        }
        response = self.app.post(
            "/api/v1.0/login",
            data=json.dumps(login),
            content_type="application/json",
        )
        data = json.loads(response.data)
        token = data['token']

        headers = {
            'Authorization': token
        }

        response = self.app.get(
            "/api/v1.0/json/99999",
            headers=headers,
            content_type="application/json",
        )

        data = json.loads(response.data)
        self.assertEqual(404, response.status_code)
        self.assertIn('code', data)
        self.assertIn('message', data)
        self.assertEqual(notFound.format("JSON"), data['message'])

    def test_json_no_permission(self):
        login = {
            "login": self.users[0]["login"],
            "password": self.users[0]["password"]
        }
        response = self.app.post(
            "/api/v1.0/login",
            data=json.dumps(login),
            content_type="application/json",
        )
        data = json.loads(response.data)
        token = data['token']

        headers = {
            'Authorization': token
        }

        response = self.app.get(
            "/api/v1.0/json/{}".format(self._json[0]['id']),
            headers=headers,
            content_type="application/json",
        )

        data = json.loads(response.data)
        self.assertEqual(404, response.status_code)
        self.assertIn('code', data)
        self.assertIn('message', data)
        self.assertEqual(permission, data['message'])
