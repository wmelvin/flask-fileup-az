from flask_wtf import FlaskForm

from wtforms import (
    BooleanField,
    SubmitField,
)


class LoginFormMsal(FlaskForm):
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign in")
