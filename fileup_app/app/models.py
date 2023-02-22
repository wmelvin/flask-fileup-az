from datetime import datetime

#  As of 2023-01-20, the User object is only created in get_current_user() in
#  auth/routes.py. The session_user comes from session["user"] (Flask var)
#  which is set to the value for the msal.ConfidentialClientApplication
#  "id_token_claims" key.


class User:
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

    def has_role(self, role_name: str) -> bool:
        roles = self._session_user.get("roles")
        if roles:
            assert isinstance(roles, list)
            return any(role == role_name for role in roles)
        return False


class UploadedFile:
    def __init__(
        self,
        upload_filename: str,
        raw_filename: str,
        user_name: str,
        storage_name: str,
        uploaded_utc: datetime,
    ):
        self.upload_filename = upload_filename
        self.raw_filename = raw_filename
        self.user_name = user_name
        self.storage_name = storage_name
        self.uploaded_utc = uploaded_utc

    def __repr__(self) -> str:
        return f"<UploadedFile '{self.user_name}':'{self.upload_filename}'>"

    def as_entity(self):
        row_key = f"{self.user_name}:{self.upload_filename}"
        result = {
            "PartitionKey": "UploadedFile",
            "RowKey": row_key,
            "UploadFileName": self.upload_filename,
            "RawFileName": self.raw_filename,
            "User": self.user_name,
            "UploadedUTC": self.uploaded_utc,
        }
        return result
