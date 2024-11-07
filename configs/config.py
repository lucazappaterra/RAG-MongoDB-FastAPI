import configparser

def load_config(file_path):
    config = configparser.ConfigParser()
    config.read(file_path)
    return config

# Example usage
config = load_config('./configs/config.ini')

MONGO_HOST = config['MONGODB']['HOST']
MONGO_PORT = int(config['MONGODB']['PORT'])
DOCS_DB = config['MONGODB']['DOCS_DB']
DOCS_COLLECTION = config['MONGODB']['DOCS_COLLECTION']

MODEL_API_BASE = config['MODEL']['API_BASE']

print(type(MONGO_HOST), type(MONGO_PORT), type(DOCS_DB), type(DOCS_COLLECTION), type(MODEL_API_BASE))
