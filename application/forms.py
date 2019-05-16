from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.fields.html5 import DateField

fields = {'string': StringField, 'date': DateField}

class DynamicForm(FlaskForm):
    def __init__(self):
        super().__init__()
