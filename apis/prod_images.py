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
def upload_product_photo(product_id, seller_id, image):
    try:
        # print("Trying to upload file")
        # print([i for i in s3.buckets.all()])
        #Get the file name
        bucket = "scalable-final-products"
        timestamp = datetime.utcnow().isoformat()
        filename = f"{seller_id}-{product_id}-{timestamp}-{image.filename}"
        # print(f'bucket: {bucket}, filename: {filename}, timestamp: {timestamp}')
        
        # client.upload_file(image, bucket, filename)
        # s3.create_bucket(Bucket=bucket)
        s3.Bucket(bucket).Object(filename).put(Body=image.read())

        print('Uploaded file to S3')


        #no longer using presign_url, return regular url
        # presign_url = s3.meta.client.generate_presigned_url(
        #     'get_object',
        #     Params={'Bucket': bucket, 'Key': filename},
        #     ExpiresIn=3600
        # )
        return get_public_s3_url(filename)
    except Exception as e:
        return {"error": str(e)}


def get_public_s3_url(filename):
    return f"{os.environ.get('S3_ENDPOINT_URL')}{filename}"



# def _get_public_s3_url(s3_presigned_url: str):
#     url = list(urlsplit(s3_presigned_url))
#     s3_public_split = urlsplit(os.environ.get('S3_ENDPOINT_URL'))
#     url[1] = f"{s3_public_split.hostname}{s3_public_split.path}"
#     return urlunsplit(url)