from azure.core.exceptions import ResourceExistsError
from azure.identity import DefaultAzureCredential
from azure.data.tables import TableServiceClient, TableClient

from flask import current_app

from app.storage.settings import get_storage_connstr, get_storage_acct_url


def create_uploads_table() -> TableClient:
    try:
        conn_str = get_storage_connstr()
        if conn_str:
            service_client = TableServiceClient.from_connection_string(
                conn_str=conn_str
            )
        else:
            acct_url = get_storage_acct_url("table")
            if acct_url:
                default_cred = DefaultAzureCredential()
                service_client: TableServiceClient = TableServiceClient(
                    acct_url, credential=default_cred
                )
            else:
                return None

        table_client = service_client.create_table_if_not_exists(
            table_name="Uploads"
        )

        return table_client
    except Exception as ex:
        # TODO: Confirm error logging.
        current_app.logger.exception("create_uploads_table")
        print("Exception:")
        print(ex)
        return None


def insert_into_uploads_table(upload_entity) -> str:
    """
    Returns an error message, or an empty string if no errors.
    """
    uploads_table = create_uploads_table()
    if not uploads_table:
        # TODO: Log error.
        return "Failed to access Uploads table."

    try:
        response = uploads_table.create_entity(upload_entity)
        print(response)
    except ResourceExistsError:
        #  Do not return this error, but do log it.
        # print(f"Entity already exists for {upload_entity}")
        current_app.logger.warn(f"Entity already exists for {upload_entity}")

    return ""
