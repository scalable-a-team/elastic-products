import os, sys
import config
import json
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)
import boto3
from datetime import datetime
from urllib.parse import urlsplit, urlunsplit

s3 = boto3.resource(**config.s3_config)

#Upload photo to bucket and return the url
def upload_product_photo(product: json, image):
    try:
        print("Trying to upload file")
        #Get the file name
        bucket = product['_product_id']
        timestamp = datetime.utcnow().isoformat()
        filename = f"{timestamp}"
        print(f'bucket: {bucket}, filename: {filename}, timestamp: {timestamp}')

        s3.Bucket(bucket).put_object(Key=filename, Body=image)

        print('Uploaded file to S3')

        presign_url = s3.meta.client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket, 'Key': filename},
            ExpiresIn=3600
        )
        return _get_public_s3_url(presign_url)
    except Exception as e:
        return {"error": str(e)}


def _get_public_s3_url(s3_presigned_url: str):
    url = list(urlsplit(s3_presigned_url))
    s3_public_split = urlsplit(os.environ.get('S3_ENDPOINT_URL'))
    # s3_public_split = urlsplit("https://tanpantz.com:9000")
    url[1] = f"{s3_public_split.hostname}{s3_public_split.path}"
    return urlunsplit(url)