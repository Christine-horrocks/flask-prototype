import requests

from flask import Flask, render_template, current_app
from flask_wtf import FlaskForm
from wtforms import StringField, DateField
from application.config import Config


app = Flask(__name__)
app.config.from_object(Config)

@app.route('/')
def index():
    print(current_app.config)
    resp = requests.get(current_app.config['SCHEMA_API_URL'])
    resp.raise_for_status()
    print(resp.json())
    schemas = [schema['name'] for schema in resp.json()]
    print(schemas)
    return render_template('index.html', schemas=schemas)


@app.route('/<schema>')
def dynamic_form(schema):

    from application.forms import DynamicForm
    from application.forms import fields

    schema_url = f"{current_app.config['SCHEMA_URL']}/{schema}-schema.json"
    schema_json = requests.get(schema_url).json()

    for field in schema_json.get('fields'):
        field_type = fields.get(field.get('type'))
        if field_type is not None:
            f = field_type(field['title'])
            setattr(DynamicForm, field['title'].lower().replace(' ', '-'), f)
            form = DynamicForm()

    return render_template('dynamicform.html', form=form)
