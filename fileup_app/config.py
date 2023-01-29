import os

from dotenv import load_dotenv


basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


class Config(object):
    FILEUP_VERSION = "230129.1"

    SECRET_KEY = os.environ.get("FILEUP_SECRET_KEY") or "this-secret-key-SUCKS"
    # TODO: Make sure the 'or' case does not make it to prod.

    ENABLE_FEATURES = os.environ.get("FILEUP_ENABLE_FEATURES", "")

    #  -- Configuration for file uploads.

    #  Default is 2MB for max size of uploaded file.
    s = os.environ.get("FILEUP_MAX_UPLOAD_MB")
    if s is not None and s.isdigit():
        max_upload_mb = int(s)
    else:
        max_upload_mb = 2

    MAX_CONTENT_LENGTH = max_upload_mb * 1024 * 1024

    UPLOAD_ACCEPT = os.environ.get("FILEUP_UPLOAD_ACCEPT") or ".csv,.xls,.xlsx"
    UPLOAD_PATH = os.environ.get("FILEUP_UPLOAD_PATH") or "uploads"

    # -- Configuration for MSAL.

    MSAL_REDIRECT_PATH = os.environ.get("FILEUP_MSAL_REDIRECT_PATH", "")
    MSAL_AUTHORITY = os.environ.get("FILEUP_MSAL_AUTHORITY", "")
    MSAL_CLIENT_ID = os.environ.get("FILEUP_MSAL_CLIENT_ID", "")
    MSAL_CLIENT_SECRET = os.environ.get("FILEUP_MSAL_CLIENT_SECRET", "")

    MSAL_SCOPE = [os.environ.get("FILEUP_MSAL_SCOPE", "")]
    #  SCOPE needs to be a list.

    # -- Configuration for Azure Storage.

    STORAGE_CONTAINER = os.environ.get("FILEUP_STORAGE_CONTAINER") or "fileup"

    STORAGE_ACCOUNT_NAME = os.environ.get("FILEUP_STORAGE_ACCOUNT_NAME", "")

    STORAGE_ACCOUNT_KEY = os.environ.get("FILEUP_STORAGE_ACCOUNT_KEY", "")

    STORAGE_ENDPOINT_SUFFIX = os.environ.get(
        "FILEUP_STORAGE_ENDPOINT_SUFFIX", ""
    )
    # or "core.windows.net"
