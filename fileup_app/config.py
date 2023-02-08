import os

from dotenv import load_dotenv


basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


def get_env_int(var_name: str, default) -> int:
    s = os.environ.get(var_name)
    if s is not None and s.isdigit():
        return int(s)
    return default


class Config(object):
    FILEUP_VERSION = "230207.3"

    SECRET_KEY = os.environ.get("FILEUP_SECRET_KEY") or "this-secret-key-SUCKS"
    # TODO: Make sure the 'or' case does not make it to prod.

    PROXY_LEVEL = get_env_int("FILEUP_PROXY_LEVEL", 0)

    ENABLE_FEATURES = os.environ.get("FILEUP_ENABLE_FEATURES", "")

    #  -- Configuration for file uploads.

    #  Default is 2MB for max size of uploaded file.
    MAX_CONTENT_LENGTH = get_env_int("FILEUP_MAX_UPLOAD_MB", 2) * 1024 * 1024

    UPLOAD_ACCEPT = os.environ.get("FILEUP_UPLOAD_ACCEPT") or ".csv,.xls,.xlsx"
    UPLOAD_PATH = os.environ.get("FILEUP_UPLOAD_PATH") or "uploads"

    # -- Configuration for MSAL.

    MSAL_REDIRECT_PATH = (
        os.environ.get("FILEUP_MSAL_REDIRECT_PATH") or "/signin-oidc"
    )
    # TODO: Use this? Currently hard-coded as "/signin-oidc" in auth/routes.

    MSAL_AUTHORITY = os.environ.get("FILEUP_MSAL_AUTHORITY", "")
    MSAL_CLIENT_ID = os.environ.get("FILEUP_MSAL_CLIENT_ID", "")
    MSAL_CLIENT_SECRET = os.environ.get("FILEUP_MSAL_CLIENT_SECRET", "")

    MSAL_SCOPE = [os.environ.get("FILEUP_MSAL_SCOPE", "")]
    #  SCOPE needs to be a list.

    # -- Configuration for Azure Storage.

    STORAGE_ACCOUNT_NAME = os.environ.get("FILEUP_STORAGE_ACCOUNT_NAME", "")

    STORAGE_CONTAINER = os.environ.get("FILEUP_STORAGE_CONTAINER") or "fileup"

    STORAGE_TABLE = os.environ.get("FILEUP_STORAGE_TABLE", "")

    STORAGE_ACCOUNT_KEY = os.environ.get("FILEUP_STORAGE_ACCOUNT_KEY", "")

    STORAGE_ENDPOINT_SUFFIX = os.environ.get(
        "FILEUP_STORAGE_ENDPOINT_SUFFIX", ""
    )
    # or "core.windows.net"
