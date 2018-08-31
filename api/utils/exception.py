from api.utils.constants import required


class AuthRequired(Exception):
    """Handles required Authorization header"""

    def __init__(self):
        self.message = required("Authorization")
