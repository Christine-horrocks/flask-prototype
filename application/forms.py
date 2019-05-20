from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
from wtforms.fields.html5 import DateField


# TODO create more mappings for types to wtforms fields
types_to_form_fields = {'string': StringField, 'date': DateField}


def formfactory(schema):

    class DynamicForm(FlaskForm):

        def __init__(self, **kwargs):
            super().__init__(**kwargs)

    for field in schema.get('fields'):
        form_field = types_to_form_fields.get(field.get('type'))
        if form_field is not None:
            constraints = field.get('constraints')
            validators = []
            if constraints.get('required'):
                validators.append(DataRequired())
            # TODO create mappings constraints to validators to user here and append to list
            f = form_field(field['title'], validators=validators)
            setattr(DynamicForm, field['name'], f)

    return DynamicForm
