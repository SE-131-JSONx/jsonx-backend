from api.models.team import Team
from api.models.team_member_map import TeamMemberMap
from api.models.user import User
from api.utils.auth import JWT
from api.utils.constants import notFound, permission, invalid
from api.utils.responses import response_with
from api.utils import responses as resp


def validate_teams(teams):
    """Helper for validating that teams exist and the user has access to the teams.
    :param teams:
    :return: None or Error
    """
    for team in teams:
        # validate team exists
        team_exists = Team.query.filter_by(id=team).first()
        if not team_exists:
            message = notFound.format("Team")
            return response_with(resp.NOT_FOUND_HANDLER_404, message=message)

        # validate access to team
        access = TeamMemberMap.query \
            .filter_by(team=team, user=JWT.details['user_id']) \
            .first()
        if not access:
            message = permission
            return response_with(resp.NOT_FOUND_HANDLER_404, message=message)


def validate_users(users):
    """Helper for validating that users exist and that the JWT user is not present in the list
    :param users:
    :return: None or Error
    """
    for user in users:
        if user == JWT.details['user_id']:
            message = invalid.format("User")
            return response_with(resp.INVALID_INPUT_422, message=message)
        # validate user exists
        user_exists = User.query.filter_by(id=user).first()
        if not user_exists:
            message = notFound.format("User")
            return response_with(resp.NOT_FOUND_HANDLER_404, message=message)
