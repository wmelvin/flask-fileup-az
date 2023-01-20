import os

# from app.auth.routes import current_user, login_required
from app.auth.routes import login_required
from app.main import bp
from app.main.forms import UploadForm
# from app.models import Org, Purpose, User
from app.storage.routes import store_uploaded_file
from datetime import datetime
from flask import (
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.utils import secure_filename


@bp.route("/")
@bp.route("/index")
def index():
    return render_template("index.html")


@bp.route("/upload")
@login_required
def upload():
    # if not session.get("user"):
    #     return redirect(url_for("auth.login"))

    #  Get list of accepted file extensions.
    upload_accept = current_app.config["UPLOAD_ACCEPT"]
    if upload_accept:
        assert isinstance(upload_accept, str)  # TODO: remove after live test.
        accept = upload_accept
    else:
        print("No UPLOAD_ACCEPT configured. Default to '.csv'.")
        accept = ".csv"

    form = UploadForm()

    return render_template(
        "upload.html", form=form, accept=accept
    )


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

    # print(f"upload_files: user='{user}', org='{org}', purpose='{purpose}'")

    for up_file in up_files:
        #  up_file is type 'werkzeug.datastructures.FileStorage'
        file_name = secure_filename(up_file.filename)
        if file_name != "":
            file_ext = os.path.splitext(file_name)[1]

            #  The UPLOAD_ACCEPT setting is a string of comma-separated file
            #  extensions. Split it into a list for exact extension check.
            #
            upload_accept = str(current_app.config["UPLOAD_ACCEPT"]).split(",")
            if file_ext not in upload_accept:
                flash(f"Invalid file type: '{file_ext}'")
                return redirect(url_for(upload_url))

            # file_name = f"fileup-u{user.id}-{purpose.get_tag()}-{file_name}"
            # store_uploaded_file(file_name, org, user, purpose, up_file)

            dt = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

            file_name = f"upload-{dt}-{file_name}"
            store_uploaded_file(file_name, up_file)

    return redirect(url_for(upload_url))
