import json
from api.routes.tests.utils.db_operation import create_users, delete_users, delete_team_members, delete_teams
from api.utils.test_base import BaseTestCase
from faker import Faker

fake = Faker()


class TestTeam(BaseTestCase):
    users = None
    teams = []

    def setUp(self):
        super(TestTeam, self).setUp()
        self.users = create_users()

    def tearDown(self):
        delete_team_members(self.users)
        delete_teams(self.teams)
        delete_users(self.users)

    """
    Create Team
    """

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

        self.teams.append(data['team']['id'])

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

    def test_duplicate_name(self):
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

        self.teams.append(data['team']['id'])

        response = self.app.post(
            "/api/v1.0/team",
            headers=headers,
            content_type="application/json",
            data=json.dumps(team_data)
        )
        self.assertEqual(422, response.status_code)

    """
    Get Team
    """

    def test_valid_get_team(self):
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

        self.teams.append(data['team']['id'])

        response = self.app.get(
            "/api/v1.0/team/{}".format(data['team']['id']),
            headers=headers,
            content_type="application/json"
        )

        data = json.loads(response.data)
        self.assertEqual(200, response.status_code)
        self.assertIn('message', data)
        self.assertEqual(team_data['name'], data['name'])

    def test_get_team_not_found(self):
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

        self.teams.append(data['team']['id'])

        response = self.app.get(
            "/api/v1.0/team/{}".format(fake.ean13()),
            headers=headers,
            content_type="application/json"
        )

        self.assertEqual(404, response.status_code)
