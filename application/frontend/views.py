import requests
import csv
import datetime
from flask import Blueprint
from flask import render_template, current_app, url_for, request, redirect
from application.utils import update_csv, csv_view, remove_dashes, csv_dict, convert_ordered_dicts_for_dl
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

