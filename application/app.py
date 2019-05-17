import requests

from flask import Flask, render_template, current_app
from wtforms import StringField, DateField, validators
from application.config import Config
from application.forms import formfactory


app = Flask(__name__)
app.config.from_object(Config)

@app.route('/')
def index():
    resp = requests.get(current_app.config['SCHEMA_API_URL'])
    resp.raise_for_status()
    schemas = [schema['name'] for schema in resp.json()]
    return render_template('index.html', schemas=schemas)


@app.route('/<schema>')
def dynamic_form(schema):

    schema_url = f"{current_app.config['SCHEMA_URL']}/{schema}-schema.json"
    schema_json = requests.get(schema_url).json()
    form = formfactory(schema_json)

    # TODO work out where form posts to and pass to template
    return render_template('dynamicform.html', form=form)
