import requests
import csv
import datetime
from flask import Blueprint
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
    if request.method == 'POST':
        form = form_object(obj=request.form)
        if form.validate():
            update_csv(draft_file_name, form.data)
            row_count = sum(1 for row in csv_view(draft_file_name))
            return redirect(url_for('frontend.check', schema=schema, row=row_count))
    else:
        form = form_object()

    return render_template('dynamicform.html', form=form, schema=schema, title=title)


@frontend.route('/<schema>/<row>/check')
def check(schema, row):
    draft_file_name = "draft-" + schema
    index_number = int(float(row)) - 1
    data = csv_dict(draft_file_name, index_number)
    title = remove_dashes(schema)
    data_list = convert_ordered_dicts_for_dl(data)

    return render_template('check.html', data=data_list, title=title)


@frontend.route('/<schema>/<row>/edit')
def edit(schema, row):
    schema = schema
    schema_url = f"{current_app.config['SCHEMA_URL']}/{schema}-schema.json"
    schema_json = requests.get(schema_url).json()
    form_object = formfactory(schema_json)
    file_name = "draft-" + schema
    index_number = int(float(row)) - 1
    data = csv_dict(file_name, index_number)
    for k, v in data.items():
        if "date" in k and v is not None:
            data[k] = datetime.datetime.strptime(v, '%Y-%m-%d').date()
    title = "Editing the form"
    form = form_object(**data)
    print("This is the editing form")

    return render_template('dynamicform.html', form=form, schema=schema, title=title)


@frontend.route('/<schema>/<row>/complete')
def complete(schema, row):
    index_number = int(float(row)) - 1
    draft_data = csv_dict("draft-" + schema, index_number)
    final_data_array = csv_dict(schema)
    title = remove_dashes(schema)
    message = "Your entry have been added"
    if draft_data in final_data_array:
        message = 'This entry already exists'
    else:
        update_csv(schema, draft_data)
    row_count = sum(1 for row in csv_view(schema))
    data = csv_dict(schema, row_count - 1)
    data_list = convert_ordered_dicts_for_dl(data)

    return render_template('complete.html', data=data_list, title=title, message=message, schema=schema)


@frontend.route('/<schema>/table')
def table(schema):
    title = remove_dashes(schema)
    with open(f'{schema}.csv', "rt") as f:
        reader = csv.reader(f)
        i = next(reader)
        rest = [row for row in reader]
    headings = []
    for heading in i:
        headings.append(remove_dashes(heading))
    entries = []
    for entry in rest:
        entries.append(entry[:-1])
    return render_template('table.html', title=title, headings=headings[:-1], entries=entries)


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


def csv_dict(file_name, index_number=None):
    with open(f'{file_name}.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        array = []
        for row in reader:
            array.append(row)
        if index_number is not None:
            return array[index_number - 1]
        else:
            return array


def convert_ordered_dicts_for_dl(data):
    data_list = []
    for x, y in data.items():
        if x != 'csrf_token':
            key = remove_dashes(x)
            data_list.append([key, y])
    return data_list
