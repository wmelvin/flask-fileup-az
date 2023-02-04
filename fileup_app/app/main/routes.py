import os

from datetime import datetime, timezone

from flask import (
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from werkzeug.utils import secure_filename

from app.auth.routes import login_required
from app.main import bp
from app.main.forms import UploadForm
from app.storage.routes import store_uploaded_file


@bp.route("/")
@bp.route("/index")
def index():
    return render_template("index.html")


@bp.route("/version")
def version():
    flash(f"Version {current_app.config.get('FILEUP_VERSION')}")
    return render_template("index.html")


@bp.route("/upload")
@login_required
def upload():
    # if not session.get("user"):
    #     return redirect(url_for("auth.login"))

    #  Get list of accepted file extensions.
    upload_accept = current_app.config.get("UPLOAD_ACCEPT")
    if upload_accept:
        assert isinstance(upload_accept, str)  # TODO: remove after live test.
        accept = upload_accept
    else:
        # print("No UPLOAD_ACCEPT configured. Default to '.csv'.")
        current_app.logger.warning(
            "No UPLOAD_ACCEPT configured. Default to '.csv'."
        )
        accept = ".csv"

    form = UploadForm()

    return render_template("upload.html", form=form, accept=accept)


@bp.route("/upload", methods=["POST"])
@login_required
def upload_files():
    # if not session.get("user"):
    #     return redirect(url_for("auth.login"))

    upload_url = "main.upload"
    up_files = request.files.getlist("file")
    if (not up_files) or (len(up_files[0].filename) == 0):
        flash("No file(s) selected.")
        return redirect(url_for(upload_url))

    for up_file in up_files:
        #  up_file is type 'werkzeug.datastructures.FileStorage'
        file_name = secure_filename(up_file.filename)
        if file_name != "":
            file_ext = os.path.splitext(file_name)[1]

            #  The UPLOAD_ACCEPT setting is a string of comma-separated file
            #  extensions. Split it into a list for exact extension check.
            #
            upload_accept = str(
                current_app.config.get("UPLOAD_ACCEPT", "")
            ).split(",")
            if file_ext not in upload_accept:
                flash(f"Invalid file type: '{file_ext}'")
                return redirect(url_for(upload_url))

            dt_utc = datetime.now(timezone.utc)

            if "AddPrefix" in current_app.config.get("ENABLE_FEATURES", ""):
                dt_str = dt_utc.strftime("%Y%m%d_%H%M%S_%f")
                upload_filename = f"upload-{dt_str}-{file_name}"
            else:
                upload_filename = file_name

            err = store_uploaded_file(
                upload_filename, file_name, dt_utc, up_file
            )
            if err:
                current_app.logger.error(err)
                flash(err)
                return redirect(url_for("main.index"))

    return redirect(url_for(upload_url))
