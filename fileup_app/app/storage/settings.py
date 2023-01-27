
from flask import current_app


def get_storage_acct_url(endpoint: str) -> str:
    """
    Builds a Storage Account URL for the given endpoint using
    current_app.config["STORAGE_ACCOUNT_NAME"]
    The endpoint must be 'blob' or 'table'.
    """
    assert endpoint in ["blob", "table"], "get_storage_acct_url: Bad endpoint"
    acct_name = current_app.config.get("STORAGE_ACCOUNT_NAME")
    if not acct_name:
        return ""
    return f"https://{acct_name}.{endpoint}.core.windows.net"


def get_storage_connstr():
    """
    Builds a Storage Connection String using current_app.config items
    STORAGE_ACCOUNT_NAME, STORAGE_ACCOUNT_KEY, and STORAGE_ENDPOINT_SUFFIX.
    When using DefaultAzureCredential instead of a connection string,
    the STORAGE_ACCOUNT_KEY should be left blank in the configuration.
    If any of the config items are empty then an empty string is returned.
    """
    acct_name = current_app.config.get("STORAGE_ACCOUNT_NAME")
    if not acct_name:
        return ""
    acct_key = current_app.config.get("STORAGE_ACCOUNT_KEY")
    if not acct_key:
        return ""
    suffix = current_app.config.get("STORAGE_ENDPOINT_SUFFIX")
    if not suffix:
        return ""
    return (
        f"DefaultEndpointsProtocol=https;AccountName={acct_name};"
        f"AccountKey={acct_key};EndpointSuffix={suffix}"
    )
