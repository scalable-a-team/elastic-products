import os

ELASTIC_PREFIX = 'es' #IMPORTANT: This will be static prefix for frontend to querey product search engine, can just change this to change all apis

ES_HOST = 'https://search-scalable-final-proj-knlaqfap2p2aavmspdlhxboypm.ap-southeast-1.es.amazonaws.com/'
ES_PORT = '9200'
ELASTIC_URI = f'{ES_HOST}:{ES_PORT}'

# TODO: IMPORTANT: UNCOMMENT THIS BEFORE PUSHING
s3_config = {
    "service_name": "s3",
    "aws_access_key_id": os.environ.get('S3_ACCESS_KEY'),
    "aws_secret_access_key": os.environ.get('S3_SECRET'),
    "endpoint_url": os.environ.get('S3_ENDPOINT_URL'),
}
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY')