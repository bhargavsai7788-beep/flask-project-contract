import os

class Config:
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://127.0.0.1:27017/clmp_db')
    GRIDFS_URI = os.environ.get('GRIDFS_URI', 'mongodb://127.0.0.1:27017/clmp_gridfs')
    # Add other configurations like secret keys, etc.

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    # More robust logging, etc.