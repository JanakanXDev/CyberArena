from backend.models.user import User, Role


class AuthService:
    """
    Fake auth for now.
    Replace later with real auth.
    """

    _users = {
        "alice": User(id=1, username="alice", role=Role.STUDENT),
        "bob": User(id=2, username="bob", role=Role.INSTRUCTOR),
    }

    @staticmethod
    def authenticate(username: str) -> User:
        user = AuthService._users.get(username)
        if not user:
            raise PermissionError("Invalid user")
        return user
