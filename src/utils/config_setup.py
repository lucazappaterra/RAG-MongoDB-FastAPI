import configparser

def load_config(file_path):
    config = configparser.ConfigParser()
    config.read(file_path)
    return config

config = load_config('./src/configs/config.ini')

MONGO_HOST = config['MONGODB']['HOST']
MONGO_PORT = int(config['MONGODB']['PORT'])
DOCS_DB = config['MONGODB']['DOCS_DB']
DOCS_COLLECTION = config['MONGODB']['DOCS_COLLECTION']
HISTORY_DB = config['MONGODB']['HISTORY_DB']
HISTORY_COLLECTION = config['MONGODB']['HISTORY_COLLECTION']

MODEL_API_BASE = config['MODEL']['API_BASE']
