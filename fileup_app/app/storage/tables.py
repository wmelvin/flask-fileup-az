from azure.core.exceptions import ResourceExistsError
from azure.data.tables import TableServiceClient, TableClient
from flask import current_app


def create_uploads_table() -> TableClient:
    try:
        conn_str = current_app.config["TABLES_CONNECTION"]
        if not conn_str:
            # flash("Upload failed: Missing storage configuration.")
            # return redirect(url_for("main.index"))
            return None

        service_client = TableServiceClient.from_connection_string(
            conn_str=conn_str
        )

        table_client = service_client.create_table_if_not_exists(
            table_name="Uploads"
        )

        return table_client
    except Exception as ex:
        # TODO: Log error.
        print("Exception:")
        print(ex)
        return None


def insert_into_uploads_table(upload_entity):
    uploads_table = create_uploads_table()
    if not uploads_table:
        # TODO: Log error.
        return
    try:
        response = uploads_table.create_entity(upload_entity)
        print(response)
    except ResourceExistsError:
        print(f"Entity already exists for {upload_entity}")
