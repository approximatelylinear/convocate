"""
This supports REST actions for the Models collection
"""

# Stdlib
import json
import datetime
import textwrap

# 3rd party
from flask import make_response, abort

# Rasa
from rasa_nlu.training_data import load_data
from rasa_nlu.model import Trainer
from rasa_nlu import config
from rasa_nlu.model import Interpreter

# Convocate
from convocate.convocate import projects

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

def get_timestamp():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


cfg =


# Cache for models
MODELS = {}


DATA = {
    "en": {
        "en_1": {
            'name': "en_1",
            'description': "NLP pipeline 1",
            'tags': ['nlp', 'english'],
            'config': json.dumps({
                'language': 'en',
                'pipeline': [
                    { 'name': "intent_featurizer_count_vectors" },
                    { 'name': "intent_classifier_tensorflow_embedding" },
                    {
                        'name': "ner_duckling_http",
                        'url': "http://localhost:9000",
                        'dimensions': [
                            "time", "number", "amount-of-money",
                            "distance", "email", "phone-number", "url"
                            "duration"],
                    },
                ]
            }),
            'timestamp': get_timestamp()
        },
        "en_2": {
            'name': "en_2",
            'description': "NLP pipeline 2",
            'tags': ['nlp', 'english'],
            'config': json.dumps(
                {
                    'language': 'en',
                    'pipeline': [
                        {
                            'name': "nlp_spacy",
                            'model': "en_core_web_md",
                            'case_sensitive': False
                        },
                        { 'name': "intent_featurizer_count_vectors" },
                        { 'name': "intent_classifier_tensorflow_embedding" },
                        {
                            'name': "ner_duckling_http",
                            'url': "http://localhost:9000",
                            'dimensions': [
                                "time", "number", "amount-of-money",
                                "distance", "email", "phone-number", "url"
                                "duration"],
                        },
                        {
                            'name': "ner_spacy",
                        }
                    ]
                }
            ),
            'timestamp': get_timestamp()
        },
    },
    "es": {
        "es_1": {
            'name': "es_1",
            'description': "NLP pipeline 1",
            'tags': ['nlp', 'spanish'],
            'config': json.dumps({
                'language': 'es',
                'pipeline': [
                    {
                        'name': "nlp_spacy",
                        'model': "es_core_news_md",
                        'case_sensitive': False
                    },
                    { 'name': "intent_featurizer_count_vectors" },
                    { 'name': "intent_classifier_tensorflow_embedding" },
                    {
                        'name': "ner_duckling_http",
                        'url': "http://localhost:9000",
                        'dimensions': [
                            "time", "number", "amount-of-money",
                            "distance", "email", "phone-number", "url"
                            "duration"],
                    },
                    {
                        'name': "ner_spacy",
                    }
                ]
            }),
            'timestamp': get_timestamp()
        }
    }
}

class ModelExistsError(Exception):
    pass


class ProjectNotFoundError(Exception):
    pass


class ModelNotFoundError(Exception):
    pass


class ModelNotTrainedError(Exception):
    pass


class MLModel():
    def __init__(self):
        pass

    @classmethod
    def get_one(cls, project_name, model_name):
        if model_name in DATA.get(project_name, {}):
            return DATA[project_name].get(model_name)
        else:
            raise ModelNotFoundError

    @classmethod
    def get_all(cls):
        return [DATA[key] for key in sorted(DATA.keys())]

    @classmethod
    def create(cls, project_name, model):
        model_name = model.get('name', None)
        description = model.get('description', None)
        tags = model.get('tags', [])
        config = model.get('config', None)

        if project_name in DATA:
            # Case where the project exists
            if model_name is not None and model_name not in DATA[project_name]:
                # Case where the model doesn't already exist
                DATA[project_name][model_name] = {
                    'name': name,
                    'description': description,
                    'tags': tags,
                    'config': config,
                    'timestamp': get_timestamp()
                }
                return True
            else:
                # Case where the model already exists
                raise ModelExistsError
        else:
            # Case where the project doesn't exist
            raise ProjectNotFoundError

    @classmethod
    def create_and_train(cls, project_name, training_data):
        """
        Train a model

        The training data is an object with this structure:
        name: <Optional name of the model>
        description: <Optional description of the model>
        tags: <Optional list of tags for the model>
        config:
            language: <Language supported by the model>
            pipeline:
                An array of items with this structure:
                    - name: <Name of the pipeline step>
                    - <arg>: <Optional step-dependent argument>
        data:
            A json-formatted array of training data
        """
        # Try to create the model
        model_name = training_data.get('name', "model_{:%Y%m%d-%H%M%S}".format(timestamp))
        training_data['name'] = model_name
        # This step may fail with a ModelExistsError or a ProjectNotFoundError
        MLModel.create(project_name, training_data)
        model = DATA[project_name][model_name]
        # Load and validate the configuration and training data
        conf = config.load(**json.loads(training_data['config']))
        data = RasaReader().read_from_json(json.loads(training_data['data']))
        # Initialize a trainer and run training
        trainer = Trainer(conf)
        trainer.train(td)
        # Save the results
        model_directory = trainer.persist(
            os.path.join(THIS_DIR, 'projects'),
            project_name=project_name,
            fixed_model_name=model_name)
        # Save model properties
        model['model_directory'] = model_directory
        model['config'] = training_data['config']
        return model

    @clsasmethod
    def score(cls, project_name, model_name, text):
        model = MLModel.get_one(project_name, model_name)
        model_directory = model.get('model_directory')
        if not model_directory:
            raise ModelNotTrainedError
        else:
            interpreter = MODELS_CACHE.get(model_directory)
            if interpreter is None:
                interpreter = Interpreter.load(model_directory)
                MODELS_CACHE[model_directory] = interpreter
            return interpreter.parse(text)


def create_and_train(project_name, training_data):
    try:
        result = MLModel.create_and_train(project_name, training_data)
    except ModelExistsError:
        abort(406, "Model {} in Project {} already exists".format(training_data['name'], project_name))
    except ProjectNotFoundError:
        abort(404, 'Project {} not found'.format(project_name))
    else:
        return make_response(
            'Successfully created and trained model {} in project {}'.format(
                result['name'], project_name), 201)


def read_all():
    return MLModel.get_all()


def read_one(project_name, model_name):
    try:
        result = MLModel.get_one(project_name, model_name)
    except ModelNotFoundError as exc:
        abort(404, 'Model {} in Project {} not found'.format(model_name, project_name))
    else:
        return result


def create(project_name, model):
    model_name = model.get('name', None)
    try:
        result = MLModel.create(project_name, model_name)
    except ModelExistsError:
        abort(406, "Model {} in Project {} already exists".format(model_name, project_name))
    except ProjectNotFoundError:
        abort(404, 'Project {} not found'.format(project_name))
    else:
        return make_response(
            'Successfully created model {} in project {}'.format(model_name, project_name), 201)


def retrain(project_name, model_name, training_data):
    """
    Retrain a model
    """

def score(project_name, model_name):
    try:
        MLModel.score(project_name, model_name)
