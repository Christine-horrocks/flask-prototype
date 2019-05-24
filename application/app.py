import requests
import csv

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
    file_name = schema_url.split('/')
    clean_file_name = file_name.pop()[:-12]
    schema_json = requests.get(schema_url).json()
    form_object = formfactory(schema_json)

    if request.method == 'POST':
        form = form_object(obj=request.form)
        if form.validate():
            print('form is good!')
            print(form.data.values())
            # DO something with the data
            update_developer_agreement_csv(clean_file_name, form.data)
            return redirect(url_for('.index'))
    else:
        form = form_object()

    return render_template('dynamicform.html', form=form, schema=schema)


def update_developer_agreement_csv(choice, data):
    data_array = list(data.values())
    print(data_array)
    with open(f'{choice}.csv', 'a') as csvfile:
        filewriter = csv.writer(csvfile)
        filewriter.writerow(data_array)
