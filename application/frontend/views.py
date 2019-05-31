
import simplejson as simplejson
import json
import requests
import csv
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
    file_name = schema_url.split('/')
    clean_file_name = file_name.pop()[:-12]
    title = clean_file_name.replace('-', ' ').capitalize()
    schema_json = requests.get(schema_url).json()
    form_object = formfactory(schema_json)

    if request.method == 'POST':
        form = form_object(obj=request.form)
        print("form is present")
        if form.validate():
            print("form is valid!!!!!!!!!!!!!!!")
            session['form_data'] = simplejson.dumps(form.data, default=str)
            session['file_name'] = clean_file_name
            return redirect(url_for('.check'))
    else:
        form = form_object()

    return render_template('dynamicform.html', form=form, schema=schema, title=title)

@frontend.route('/check')
def check():
    data = json.loads(session.get('form_data', None))
    title = remove_dashes(session.get('file_name', None))
    data_list = []
    for x, y in data.items():
        if x != 'csrf_token':
            key = remove_dashes(x)
            data_list.append([key, y])

    return render_template('check.html', data=data_list, title=title)

@frontend.route('/complete')
def complete():
    form_data = json.loads(session.get('form_data', None))
    file_name = session.get('file_name', None)
    title = remove_dashes(file_name)
    update_csv(file_name, form_data)
    csv_data = last_line_csv_view(file_name).split()

    return render_template('complete.html', data=csv_data, title=title)



def update_csv(choice, data):
    data_array = list(data.values())
    with open(f'{choice}.csv', 'a') as csvfile:
        filewriter = csv.writer(csvfile)
        filewriter.writerow(data_array)

def last_line_csv_view(file_name):
    with open(f'{file_name}.csv') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',')
        csv_data = []
        for row in reversed(list(csv_reader)):
            csv_data.append(', '.join(row))
        return csv_data[0]

def remove_dashes(input):
    output = input.replace('-', ' ').capitalize()
    return output