import os, sys
import config
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)
import boto3
from datetime import datetime
from urllib.parse import urlsplit, urlunsplit

s3 = boto3.resource(**config.s3_config)

#Upload photo to bucket and return the url
def upload_product_photo(seller_id, image):
    try:
        #Get the file name
        bucket = "scalable-final-products"
        timestamp = datetime.utcnow().isoformat()
        filename = f"{seller_id}-{timestamp}-{image.filename}"

        s3.Bucket(bucket).Object(filename).put(Body=image.read())

        print('Uploaded file to S3')

        return get_public_s3_url(filename)
    except Exception as e:
        return {"error": str(e)}

def get_public_s3_url(filename):
    return f"{os.environ.get('S3_ENDPOINT_URL')}{filename}"
