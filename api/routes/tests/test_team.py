import json
from api.models.user import User
from api.routes.tests.utils.db_operation import create_users, delete_users, delete_team_members, delete_teams
from api.utils.constants import permission, notFound
from api.utils.database import db
from api.utils.test_base import BaseTestCase
from faker import Faker

fake = Faker()


class TestTeam(BaseTestCase):
    users = None
    teams = []

    def setUp(self):
        super(TestTeam, self).setUp()
        self.users = create_users(2)

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

    """
    Update Team
    """
    def test_valid_update_team(self):
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

        response = self.app.put(
            "/api/v1.0/team/{}".format(data['team']['id']),
            headers=headers,
            content_type="application/json",
            data=json.dumps(team_data)
        )

        data = json.loads(response.data)
        self.assertEqual(200, response.status_code)
        self.assertIn('message', data)
        self.assertEqual(team_data['name'], data['team']['name'])

    def test_update_team_not_found(self):
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

        response = self.app.put(
            "/api/v1.0/team/{}".format(fake.ean13()),
            headers=headers,
            content_type="application/json",
            data=json.dumps(team_data)
        )

        self.assertEqual(404, response.status_code)

    def test_update_team_no_permission(self):
        # Get JWT for user 0
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
        token_user_0 = data['token']

        login = {
            "login": self.users[1]["login"],
            "password": self.users[1]["password"]
        }
        response = self.app.post(
            "/api/v1.0/login",
            data=json.dumps(login),
            content_type="application/json",
        )
        data = json.loads(response.data)
        token_user_1 = data['token']

        headers = {
            'Authorization': token_user_0
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

        headers = {
            'Authorization': token_user_1
        }

        response = self.app.put(
            "/api/v1.0/team/{}".format(data['team']['id']),
            headers=headers,
            content_type="application/json",
            data=json.dumps(team_data)
        )
        data = json.loads(response.data)

        self.assertEqual(404, response.status_code)
        self.assertEqual(permission, data['message'])

    """
    Delete Team
    """
    def test_valid_delete_team(self):
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

        response = self.app.delete(
            "/api/v1.0/team/{}".format(data['team']['id']),
            headers=headers,
            content_type="application/json",
            data=json.dumps(team_data)
        )

        data = json.loads(response.data)
        self.assertEqual(200, response.status_code)
        self.assertIn('message', data)

    def test_delete_team_not_found(self):
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

        response = self.app.delete(
            "/api/v1.0/team/{}".format(fake.ean13()),
            headers=headers,
            content_type="application/json",
            data=json.dumps(team_data)
        )

        self.assertEqual(404, response.status_code)

    def test_delete_team_no_permission(self):
        # Get JWT for user 0
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
        token_user_0 = data['token']

        login = {
            "login": self.users[1]["login"],
            "password": self.users[1]["password"]
        }
        response = self.app.post(
            "/api/v1.0/login",
            data=json.dumps(login),
            content_type="application/json",
        )
        data = json.loads(response.data)
        token_user_1 = data['token']

        headers = {
            'Authorization': token_user_0
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

        headers = {
            'Authorization': token_user_1
        }

        response = self.app.delete(
            "/api/v1.0/team/{}".format(data['team']['id']),
            headers=headers,
            content_type="application/json",
            data=json.dumps(team_data)
        )
        data = json.loads(response.data)

        self.assertEqual(404, response.status_code)
        self.assertEqual(permission, data['message'])

    """
    Give Member Access
    """

    def test_give_team_access_team_not_found(self):
        # Get JWT for user 0
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
        headers = {
            'Authorization': data['token']
        }

        team_data = {
            "user": db.session.query(User.id).filter(User.login == self.users[1]['login']).scalar()
        }

        response = self.app.post(
            "/api/v1.0/team/{}/access".format(fake.ean13()),
            headers=headers,
            content_type="application/json",
            data=json.dumps(team_data)
        )
        data = json.loads(response.data)

        self.assertEqual(404, response.status_code)
        self.assertEqual(notFound.format("Team"), data['message'])

    def test_give_team_access_no_permission(self):
        # Get JWT for user 0
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
        token_user_0 = data['token']

        login = {
            "login": self.users[1]["login"],
            "password": self.users[1]["password"]
        }
        response = self.app.post(
            "/api/v1.0/login",
            data=json.dumps(login),
            content_type="application/json",
        )
        data = json.loads(response.data)
        token_user_1 = data['token']

        headers = {
            'Authorization': token_user_0
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

        headers = {
            'Authorization': token_user_1
        }

        team_data = {
            "user": db.session.query(User.id).filter(User.login == self.users[1]['login']).scalar()
        }

        response = self.app.post(
            "/api/v1.0/team/{}/access".format(data['team']['id']),
            headers=headers,
            content_type="application/json",
            data=json.dumps(team_data)
        )
        data = json.loads(response.data)

        self.assertEqual(404, response.status_code)
        self.assertEqual(permission, data['message'])

    def test_give_team_access_user_not_found(self):
        # Get JWT for user 0
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
        token_user_0 = data['token']

        headers = {
            'Authorization': token_user_0
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

        team_data = {
            "user": fake.ean13()
        }

        response = self.app.post(
            "/api/v1.0/team/{}/access".format(data['team']['id']),
            headers=headers,
            content_type="application/json",
            data=json.dumps(team_data)
        )
        data = json.loads(response.data)

        self.assertEqual(404, response.status_code)
        self.assertEqual(notFound.format("User"), data['message'])

    def test_give_team_access_valid(self):
        # Get JWT for user 0
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

        headers = {
            'Authorization': data['token']
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

        team_data = {
            "user": db.session.query(User.id).filter(User.login == self.users[1]['login']).scalar()
        }

        response = self.app.post(
            "/api/v1.0/team/{}/access".format(data['team']['id']),
            headers=headers,
            content_type="application/json",
            data=json.dumps(team_data)
        )
        self.assertEqual(200, response.status_code)

    """
    Delete Team Member Access
    """
    def test_valid_delete_team_member_access(self):
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
        self.teams.append(data['team']['id'])

        team_data = {
            "user": db.session.query(User.id).filter(User.login == self.users[1]['login']).scalar()
        }

        response = self.app.delete(
            "/api/v1.0/team/{}/access/{}".format(data['team']['id'], team_data["user"]),
            headers=headers,
            content_type="application/json",
        )

        data = json.loads(response.data)
        self.assertEqual(200, response.status_code)
        self.assertIn('message', data)

    def test_delete_team_member_access_team_not_found(self):
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

        data = json.loads(response.data)
        self.teams.append(data['team']['id'])

        team_data = {
            "user": db.session.query(User.id).filter(User.login == self.users[1]['login']).scalar()
        }

        response = self.app.delete(
            "/api/v1.0/team/{}/access/{}".format(fake.ean13(), team_data["user"]),
            headers=headers,
            content_type="application/json",
        )

        self.assertEqual(404, response.status_code)

    def test_delete_team_member_access_no_permission(self):
        # Get JWT for user 0
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
        token_user_0 = data['token']

        login = {
            "login": self.users[1]["login"],
            "password": self.users[1]["password"]
        }
        response = self.app.post(
            "/api/v1.0/login",
            data=json.dumps(login),
            content_type="application/json",
        )
        data = json.loads(response.data)
        token_user_1 = data['token']

        headers = {
            'Authorization': token_user_0
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

        headers = {
            'Authorization': token_user_1
        }

        team_data = {
            "user": db.session.query(User.id).filter(User.login == self.users[0]['login']).scalar()
        }

        response = self.app.delete(
            "/api/v1.0/team/{}/access/{}".format(data['team']['id'], team_data["user"]),
            headers=headers,
            content_type="application/json",
        )

        data = json.loads(response.data)

        self.assertEqual(404, response.status_code)
        self.assertEqual(permission, data['message'])

    def test_delete_team_member_access_user_not_found(self):
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

        data = json.loads(response.data)
        self.teams.append(data['team']['id'])

        response = self.app.delete(
            "/api/v1.0/team/{}/access/{}".format(data['team']['id'], fake.ean13()),
            headers=headers,
            content_type="application/json",
        )

        self.assertEqual(404, response.status_code)
