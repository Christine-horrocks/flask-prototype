import simplejson as simplejson
import json
import requests
import csv
import datetime
from flask import Blueprint, session
from flask import render_template, current_app, url_for, request, redirect
from application.forms import formfactory

frontend = Blueprint('frontend', __name__, template_folder='templates')


@frontend.route('/')
def index():
    resp = requests.get(current_app.config['SCHEMA_API_URL'])
    resp.raise_for_status()
    schemas = [schema['name'] for schema in resp.json()]
    return render_template('index.html', schemas=schemas)


@frontend.route('/<schema>', methods=['GET', 'POST'])
def dynamic_form(schema):
    schema_url = f"{current_app.config['SCHEMA_URL']}/{schema}-schema.json"
    draft_file_name = "draft-" + schema
    title = schema.replace('-', ' ').capitalize()
    schema_json = requests.get(schema_url).json()
    form_object = formfactory(schema_json)
    session['schema_json'] = schema_json
    session['schema'] = schema

    if request.method == 'POST':
        form = form_object(obj=request.form)
        print("Dynamic form is present")
        if form.validate():
            print("Dynamic form is valid!!!!!!!!!!!!!!!")
            update_csv(draft_file_name, form.data)
            row_count = sum(1 for row in csv_view(draft_file_name))
            session['form_data'] = simplejson.dumps(form.data, default=str)
            session['file_name'] = schema
            return redirect(url_for('frontend.check', schema=schema, row=row_count))
    else:
        form = form_object()

    return render_template('dynamicform.html', form=form, schema=schema, title=title)


@frontend.route('/<schema>/<row>/check')
def check(schema, row):
    file_name = "draft-" + schema
    index_number = int(float(row)) - 1
    data = csv_dict(file_name, index_number)
    title = remove_dashes(schema)
    data_list = []
    for x, y in data.items():
        if x != 'csrf_token':
            key = remove_dashes(x)
            data_list.append([key, y])

    return render_template('check.html', data=data_list, title=title)


@frontend.route('/edit')
def edit():
    schema = session.get('schema', None)
    schema_json = session.get('schema_json', None)
    form_object = formfactory(schema_json)
    data = json.loads(session.get('form_data', None))
    for k, v in data.items():
        if "date" in k and v is not None:
            data[k] = datetime.datetime.strptime(v, '%Y-%m-%d').date()

    title = "Editing the form"
    form = form_object(**data)
    print("This is the editing form")

    return render_template('dynamicform.html', form=form, schema=schema, title=title)


@frontend.route('/complete')
def complete():
    form_data = json.loads(session.get('form_data', None))
    file_name = session.get('file_name', None)
    title = remove_dashes(file_name)
    update_csv(file_name, form_data)
    csv_data = csv_view(file_name)[0].split()

    return render_template('complete.html', data=csv_data, title=title)


def update_csv(file_name, data):
    data_array = list(data.values())
    with open(f'{file_name}.csv', 'a') as csvfile:
        filewriter = csv.writer(csvfile)
        filewriter.writerow(data_array)


def csv_view(file_name):
    with open(f'{file_name}.csv') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',')
        csv_data = []
        for row in reversed(list(csv_reader)):
            csv_data.append(', '.join(row))
        return csv_data


def remove_dashes(input):
    output = input.replace('-', ' ').capitalize()
    return output


def csv_dict(file_name, index_number):
    with open(f'{file_name}.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        array = []
        for row in reader:
            array.append(row)
        return array[index_number - 1]
