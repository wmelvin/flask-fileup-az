from flask_wtf import FlaskForm

# from wtforms import (SubmitField, MultipleFileField, RadioField)
from wtforms import (SubmitField, MultipleFileField)

from wtforms.validators import DataRequired


class UploadForm(FlaskForm):
    file = MultipleFileField("Select file(s)", validators=[DataRequired()])
    # purpose = RadioField("Purpose of File(s)", validators=[DataRequired()])
    submit = SubmitField("Upload")
