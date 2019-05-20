import requests

from flask import Flask, render_template, current_app, url_for, request, redirect
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


@app.route('/<schema>', methods=['GET', 'POST'])
def dynamic_form(schema):

    schema_url = f"{current_app.config['SCHEMA_URL']}/{schema}-schema.json"
    schema_json = requests.get(schema_url).json()
    form_object = formfactory(schema_json)

    if request.method == 'POST':
        form = form_object(obj=request.form)
        if form.validate():
            print('form is good!')
            print(form.data)
            # DO something with the data
            return redirect(url_for('.index'))
    else:
        form = form_object()

    return render_template('dynamicform.html', form=form, schema=schema)
