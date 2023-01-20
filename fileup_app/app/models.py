
#  As of 2023-01-20, the User object is only created in get_current_user() in
#  auth/routes.py. The session_user comes from (Flask.) session["user"].

class User():
    def __init__(self, session_user=None):
        self.session_user = session_user

    def __repr__(self) -> str:
        return f"<User {self.id}: '{self.username}'>"

    @property
    def is_active(self):
        #  Default to True if session_user is set.
        return self.session_user is not None

    @property
    def is_anonymous(self):
        return self.session_user is None

    @property
    def is_authenticated(self):
        return self.session_user is not None
