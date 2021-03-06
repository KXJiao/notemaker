import os
from os.path import join, dirname, realpath
from flask import Flask
from . import summary


UPLOAD_FOLDER = '/tmp/'



def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'researchtime.sqlite'),
    )

    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass


    app.register_blueprint(summary.bp)
    app.add_url_rule('/', endpoint='index')

    return app
