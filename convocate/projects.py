"""
This supports REST actions for the Projects collection
"""

# Stdlib
import os
import datetime

# 3rd party
from flask import make_response, abort

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

def get_timestamp():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

DATA = {
    "en": {
        'name': "en",
        'description': "English NLP pipeline",
        'tags': ['nlp', 'english'],
        'timestamp': get_timestamp(),
        'path': os.path.join(THIS_DIR, 'projects', 'en')
    },
    "es": {
        'name': "es",
        'description': "Spanish NLP pipeline",
        'tags': ['nlp', 'spanish'],
        'timestamp': get_timestamp(),
        'path': os.path.join(THIS_DIR, 'projects', 'es')
    }
}

def read_all():
    return [DATA[key] for key in sorted(DATA.keys())]


def read_one(name):
    if name in DATA:
        return DATA.get(name)
    else:
        abort(404, 'Project with name {} not found'.format(name))


def create(project):
    name = project.get('name', None)
    description = project.get('description', None)
    tags = project.get('tags', [])
    if name not in DATA and name is not None:
        DATA[name] = {
            'name': name,
            'description': description,
            'tags': tags,
            'timestamp': get_timestamp()
        }
        return make_response('{} successfully created'.format(name), 201)
    else:
        abort(406, "Person with name {} already exists".format(name))


def update(name, project):
    if name in DATA:
        DATA[name]['description'] = project.get('description', DATA[name]['description'])
        DATA[name]['tags'] = project.get('tags', DATA[name]['tags'])
        DATA[name]['timestamp'] = get_timestamp()
        return DATA[name]
    else:
        abort(404, 'Project with name {} not found'.format(name))


def delete(name):
    if name in DATA:
        del DATA[name]
        return make_response('{} successfully deleted'.format(name), 200)
    else:
        abort(404, 'Project with name {} not found'.format(name))
