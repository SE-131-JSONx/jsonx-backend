import json
from api.routes.tests.utils.db_operation import create_users, delete_users
from api.utils.test_base import BaseTestCase
from faker import Faker

fake = Faker()


class TestTeam(BaseTestCase):
    users = None

    def setUp(self):
        super(TestTeam, self).setUp()
        self.users = create_users()

    def tearDown(self):
        delete_users(self.users)

    def test_valid_create_team(self):
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

        team_data = {
            "name": fake.company()
        }
        response = self.app.post(
            "/api/v1.0/team",
            headers=headers,
            content_type="application/json",
            data=json.dumps(team_data)
        )

        data = json.loads(response.data)
        self.assertEqual(200, response.status_code)
        self.assertIn('message', data)
        self.assertIn('team', data)
        self.assertEqual(team_data['name'], data['team']['name'])

    def test_required_name(self):
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

        team_data = {
            "not_name": "1"
        }
        response = self.app.post(
            "/api/v1.0/team",
            headers=headers,
            content_type="application/json",
            data=json.dumps(team_data)
        )
        self.assertEqual(422, response.status_code)

    def test_invalid_name(self):
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

        team_data = {
            "not_name": 1.233
        }
        response = self.app.post(
            "/api/v1.0/team",
            headers=headers,
            content_type="application/json",
            data=json.dumps(team_data)
        )
        self.assertEqual(422, response.status_code)
