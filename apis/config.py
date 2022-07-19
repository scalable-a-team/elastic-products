import os
from accesskeys.acess_keys import *


ELASTIC_PREFIX = 'es' #IMPORTANT: This will be static prefix for frontend to querey product search engine, can just change this to change all apis
PRODUCT_LISTING_PREFIX = 'products'
user = os.environ.get('POSTGRES_USER')
password = os.environ.get('POSTGRES_PASSWORD')
host = os.environ.get('POSTGRES_HOST')


POSTGRES_DATABASE = f"postgresql://{user}:{password}@{host}"

ES_HOST = os.environ.get('ES_HOST')
ES_PORT = os.environ.get('ES_PORT')

ELASTIC_URI = f'{ES_HOST}:{ES_PORT}'

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY')

s3_config = {
    "service_name": "s3",
    "aws_access_key_id": AWS_ACCESS_KEY_ID,
    "aws_secret_access_key": AWS_SECRET_KEY,
    "endpoint_url": os.environ.get('S3_ENDPOINT_URL'),
}

