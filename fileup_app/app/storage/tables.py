from azure.data.tables import TableServiceClient, TableClient

# from flask import current_app, flash, redirect, url_for
from flask import current_app


def create_uploads_table() -> TableClient:
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
