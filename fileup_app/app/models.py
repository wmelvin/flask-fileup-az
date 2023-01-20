
#  As of 2023-01-20, the User object is only created in get_current_user() in
#  auth/routes.py. The session_user comes from session["user"] (Flask var)
#  which is set to the value for the msal.ConfidentialClientApplication
#  "id_token_claims" key.

class User():
    def __init__(self, session_user=None):
        self._session_user = session_user

    def __repr__(self) -> str:
        return f"<User '{self.name}' ({self.preferred_username})>"

    @property
    def preferred_username(self):
        if self._session_user:
            return self._session_user.get("preferred_username")
        return None

    @property
    def name(self):
        if self._session_user:
            return self._session_user.get("name")
        return None

    @property
    def subject(self):
        if self._session_user:
            return self._session_user.get("sub")
        return None

    @property
    def is_active(self):
        #  Default to True if session_user is set.
        return self._session_user is not None

    @property
    def is_anonymous(self):
        return self._session_user is None

    @property
    def is_authenticated(self):
        return self._session_user is not None
