#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
from api.models.user import User
from api.utils.database import db
from api.utils.test_base import BaseTestCase
from faker import Faker

fake = Faker()


def create_users():
    users = [{
        "name": fake.first_name(),
        "surname": fake.last_name(),
        "email": fake.ascii_company_email(),
        "login": fake.user_name(),
        "password": fake.bban()
    }]
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
