from flask import Flask
from flask_pymongo import PyMongo
from config import DevelopmentConfig, ProductionConfig
import gridfs
import os
from flask_restx import Api
from app.api.routes import api as contracts_ns

mongo = PyMongo()  # Initialize PyMongo outside the factory

def create_app(config_class=None):
    if config_class is None:
        env = os.environ.get('FLASK_ENV', 'development')
        if env == 'production':
            config_class = ProductionConfig
        else:
            config_class = DevelopmentConfig

    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize MongoDB with app context
    mongo.init_app(app)
    app.mongo_client = mongo.cx # type: ignore
    app.db = mongo.db # type: ignore
    app.gridfs = gridfs.GridFS(app.db) # type: ignore
    
    # Flask-RESTX API and namespace
    api = Api(app)
    api.add_namespace(contracts_ns, path='/api/contracts')

    return app

