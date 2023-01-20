import uuid
import msal

from app.auth.forms import LoginFormMsal
from app.models import User

from flask import (
    Blueprint,
    current_app,
    flash,
    has_request_context,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from functools import wraps
# from itsdangerous.url_safe import URLSafeSerializer
from werkzeug.local import LocalProxy


# MAX_AGE_SEC = 60 * 60 * 24 * 90  # Set cookie max_age in seconds to 90 days.


bp = Blueprint("auth", __name__, template_folder="templates")

current_user = LocalProxy(lambda: get_current_user())


def login_required(f):
    @wraps(f)
    def _login_required(*args, **kwargs):
        if current_user.is_anonymous:
            flash("Please sign in to access the requested page.", "danger ")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return _login_required


@bp.route("/login", methods=["GET", "POST"])
def login():
    #  Route to sign in with Azure Active Directory.

    form = LoginFormMsal()

    if form.validate_on_submit():  # Always returns False for GET request.
        scopes = current_app.config["MSAL_SCOPE"]

        #  The 'state' value is returned in the response to the redirect URI.
        #  Encode the remember-me setting in the first character.
        if form.remember_me.data:
            session["state"] = f"1{str(uuid.uuid4())}"
        else:
            session["state"] = f"0{str(uuid.uuid4())}"

        auth_url = _build_auth_url(scopes=scopes, state=session["state"])

        return redirect(auth_url)

    return render_template("login.html", form=form)


@bp.route("/signin-oidc")
def authorized():
    s = session.get("state")
    if request.args.get("state") != s:
        return redirect(url_for("index"))

    # #  The 'remember-me' choice is encoded in the first character of the
    # #  'state' value.
    # do_remember = s and str(s).startswith("1")

    if "error" in request.args:
        return render_template("auth_error.html", result=request.args)

    if request.args.get("code"):
        cache = _load_cache()
        result = _build_msal_app(
            cache=cache
        ).acquire_token_by_authorization_code(
            request.args["code"],
            scopes=current_app.config["MSAL_SCOPE"],
            redirect_uri=url_for("auth.authorized", _external=True),
        )
        if "error" in result:
            return render_template("auth_error.html", result=result)

        user_claims = result.get("id_token_claims")

        session["user"] = user_claims

        _save_cache(cache)

        # if user and do_remember:
        #     return get_response_to_remember(user)

    return redirect(url_for("main.index"))


@bp.route("/logout")
@login_required
def logout():
    session.clear()
    uri = current_app.config["MSAL_AUTHORITY"]
    uri += "/oauth2/v2.0/logout?post_logout_redirect_uri="
    uri += url_for("main.index", _external=True)
    return redirect(uri)


@bp.app_context_processor
def inject_current_user():
    if has_request_context():
        return dict(current_user=get_current_user())
    return dict(current_user="")


def get_current_user():
    # TODO: This seems like it's is basically a stub. Do more here?
    _current_user = User(session.get("user"))
    return _current_user


# def encrypt_cookie(content):
#     zer = URLSafeSerializer(current_app.config["SECRET_KEY"])
#     enc = zer.dumps(content)
#     return enc


# def decrypt_cookie(enc):
#     zer = URLSafeSerializer(current_app.config["SECRET_KEY"])
#     try:
#         content = zer.loads(enc)
#     except:  # noqa E722
#         content = "-1"
#     return content


def _build_msal_app(cache=None, authority=None):
    return msal.ConfidentialClientApplication(
        current_app.config["MSAL_CLIENT_ID"],
        authority=authority or current_app.config["MSAL_AUTHORITY"],
        client_credential=current_app.config["MSAL_CLIENT_SECRET"],
        token_cache=cache,
    )


def _build_auth_url(authority=None, scopes=None, state=None):
    msal_app = _build_msal_app(authority=authority)

    auth_url = msal_app.get_authorization_request_url(
        scopes or [],
        state=state or str(uuid.uuid4()),
        redirect_uri=url_for("auth.authorized", _external=True),
    )

    return auth_url


# TODO: Implement MSAL cache some other way. It will not fit in a cookie.


def _load_cache():
    cache = msal.SerializableTokenCache()
    # if session.get("token_cache"):
    #     cache.deserialize(session["token_cache"])
    return cache


def _save_cache(cache):
    # if cache.has_state_changed:
    #     session["token_cache"] = cache.serialize()
    return
