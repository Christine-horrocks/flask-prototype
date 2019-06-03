from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField
from wtforms.validators import ValidationError, DataRequired, Optional, URL, Email
from wtforms.fields.html5 import DateField


# TODO create more mappings for types to wtforms fields
types_to_form_fields = {'string': StringField, 'date': DateField, 'number': DecimalField}


def formfactory(schema):

    class DynamicForm(FlaskForm):

        def __init__(self, **kwargs):
            super().__init__(**kwargs)

    for field in schema.get('fields'):
        form_field = types_to_form_fields.get(field.get('type'))
        if form_field is not None:
            constraints = field.get('constraints')
            validators = []
            if field.get('format') is not None:
                validators.append(type_validators(field.get('format')))
            if constraints.get('required'):
                validators.append(DataRequired(message="This field is required and must be in the correct form"))
            else:
                validators.append(Optional(strip_whitespace=True))

            f = form_field(field['title'], validators=validators)
            setattr(DynamicForm, field['name'], f)

    return DynamicForm

def type_validators(type):
    if type is not None:
        return {
            "uri" : URL(message="This is not a valid URL"),
            "email" : Email(message="This is not a valid email address")
        }[type]

def validators_builder(self, field):
    constraints = field.get('constraints')
    validators = []
    if field.get('format') is not None:
        validators.append(type_validators(self, field.get('format')))
    if constraints.get('required'):
        validators.append(DataRequired(message="This field is required"))
    else:
        validators.append(Optional(strip_whitespace=True))
    return validators
