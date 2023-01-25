import os
import tempfile

from datetime import datetime, timezone
from pathlib import Path

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobClient, BlobServiceClient, ContainerClient
from flask import Blueprint, current_app, flash, redirect, url_for
from werkzeug.datastructures import FileStorage

from app.storage.settings import get_storage_acct_url, get_storage_connstr
from app.storage.tables import create_uploads_table, insert_into_uploads_table
from app.auth.routes import current_user
from app.models import UploadedFile, User


bp = Blueprint("storage", __name__, template_folder="templates")


class CheckStorageError(Exception):
    pass


def store_uploaded_file(
    upload_filename: str,
    raw_filename: str,
    uploaded_utc: datetime,
    file_data: FileStorage,
) -> str:
    """
    If Azure Storage is configured, the uploaded file will be stored
    in a blob container. Otherwise the uploaded file is written to
    the UPLOAD_PATH on the host.

    After the file is stored, a UploadedFile record is inserted in
    the database.

    Returns an error message, or an empty string if no errors.
    """
    err = ""
    if (current_app.config["STORAGE_ACCOUNT_NAME"]):
        storage_name = (
            f"AzureContainer:{current_app.config['STORAGE_CONTAINER']}"
        )

        # TODO: Perhaps storage_name should hold the blob URL for the uploaded
        #  file, depenging on what any downstream processing needs. The column
        #  type might need to be larger than the current String(255).

        err = _saveToBlob(upload_filename, file_data)
    else:
        upload_path = current_app.config["UPLOAD_PATH"]
        storage_name = f"FileSystem:{upload_path}"
        file_data.save(os.path.join(upload_path, upload_filename))

    if not err:
        user: User = current_user
        if user:
            user_name = user.preferred_username
        else:
            ds = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_%f')
            user_name = f"UNKNOWN_USER_{ds}"
            # print(f"store_uploaded_file: {user_name}")  # TODO: Log this.
            current_app.logger.info(f"store_uploaded_file: {user_name}")

        uf: UploadedFile = UploadedFile(
            upload_filename,
            raw_filename,
            user_name,
            storage_name,
            uploaded_utc,
        )

        err = insert_into_uploads_table(uf.as_entity())

    return err


def _saveToBlob(file_name: str, file_data: FileStorage) -> str:
    """
    Returns an error message, or an empty string if no errors.
    """
    try:
        conn_str = get_storage_connstr()
        if conn_str:
            service_client: BlobServiceClient = (
                BlobServiceClient.from_connection_string(conn_str)
            )
        else:
            acct_url = get_storage_acct_url("blob")
            if acct_url:
                default_cred = DefaultAzureCredential()
                service_client: BlobServiceClient = BlobServiceClient(
                    acct_url, credential=default_cred
                )
            else:
                return "Upload failed: Missing storage configuration."

        container_name = current_app.config["STORAGE_CONTAINER"]

        container_client: ContainerClient = (
            service_client.get_container_client(container_name)
        )
        if container_client.exists():
            # print(f"Container exists: '{container_client.container_name}'")
            current_app.logger.info(
                f"Container exists: '{container_client.container_name}'"
            )
        else:
            container_client: ContainerClient = (
                service_client.create_container(container_name)
            )
            # print(f"Created container: '{container_client.container_name}'")
            current_app.logger.info(
                f"Created container: '{container_client.container_name}'"
            )

        blob_client: BlobClient = container_client.get_blob_client(
            blob=file_name
        )

        if blob_client.exists():
            # print(f"Blob exists: '{blob_client.blob_name}'")
            current_app.logger.info(f"Blob exists: '{blob_client.blob_name}'")
        else:
            blob_client.upload_blob(file_data)

        return ""

    except Exception:
        # print("Exception:")
        # print(ex)
        current_app.logger.exception("_saveToBlob failed")
        return "Exception - upload failed"


@bp.route("/checkstorage", methods=["GET"])
def check_storage():
    if "CheckStorage" not in current_app.config["ENABLE_FEATURES"]:
        return redirect(url_for("main.index"))

    try:
        step = "Requesting service client."
        current_app.logger.info(f"CheckStorage: {step}")
        acct_url = current_app.config["STORAGE_ACCOUNT_URL"]
        if acct_url:
            default_cred = DefaultAzureCredential()
            service_client: BlobServiceClient = BlobServiceClient(
                acct_url, credential=default_cred
            )
        else:
            conn_str = current_app.config["STORAGE_CONNECTION"]
            if not conn_str:
                flash("CheckStorage: Not configured to access storage.")
                return redirect(url_for("main.index"))

            service_client: BlobServiceClient = (
                BlobServiceClient.from_connection_string(conn_str)
            )

        container_name = "fileup"

        step = "Requesting container client."
        current_app.logger.info(f"CheckStorage: {step}")
        container_client: ContainerClient = (
            service_client.get_container_client(container_name)
        )
        if container_client.exists():
            current_app.logger.info(
                f"Container exists: '{container_client.container_name}'"
            )
        else:
            container_client: ContainerClient = (
                service_client.create_container(container_name)
            )
            current_app.logger.info(
                f"Created container: '{container_client.container_name}'"
            )

        test_file = Path(tempfile.gettempdir()) / "fileup-test.txt"

        step = "Requesting blob client."
        current_app.logger.info(f"CheckStorage: {step}")
        blob_client: BlobClient = container_client.get_blob_client(
            blob=test_file.name
        )

        if blob_client.exists():
            current_app.logger.info(f"Blob exists: '{blob_client.blob_name}'")
        else:
            test_file.write_text("Testing...")
            with open(test_file, "rb") as f:
                blob_client.upload_blob(f)

        step = "Requesting Uploads table."
        current_app.logger.info(f"CheckStorage: {step}")
        if current_app.config["TABLES_CONNECTION"]:
            result = create_uploads_table()
            if result:
                current_app.logger.info(f"OK: {result.table_name}")
            else:
                raise CheckStorageError("Cannot access Uploads table.")
        else:
            current_app.logger.info("(skip) TABLES_CONNECTION not set.")

    except Exception as ex:
        current_app.logger.exception(f"CheckStorage: Failed at '{step}'")
        print("Exception:")
        print(ex)
        flash(f"CheckStorage: Failed at '{step}'")
        return redirect(url_for("main.index"))

    flash("CheckStorage: OK.")
    return redirect(url_for("main.index"))
