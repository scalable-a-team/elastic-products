from os import write
from flask import Flask, jsonify, request, json
from prod_images import upload_product_photo
from config import *
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from accesskeys.aws_secrets import * #This is hidden from github, but you can use this to store your AWS credentials


app = Flask(__name__)
es = Elasticsearch(
    hosts=ES_HOST,
    http_auth=AWS4Auth(AWS_ACCESS_KEY_ID, AWS_SECRET_KEY, 'ap-southeast-1', 'es'), #For signing the request to Elasticsearch
    verify_certs=True,
    use_ssl=True,
    connection_class=RequestsHttpConnection,
    port=443
)

#PRODUCT LISTING CHARACTERISTICS
"""
A product is made up of
product_id: int
supplier_id: int
description: varchar
price: float
image_url: varchar ***maybe an array of varchars, for multiple pictures***
"""

example_product = {
    "_product_id": 1,
    "_supplier_id": 1,
    "description": "This is a test product",
    "price": 1.00,
    "image_url": "https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png"
}

#create product
@app.route(f'/{ELASTIC_PREFIX}/create', methods=['POST'])
def publish():
    resp = {}
    try:
        content = request.json
        doc = content['product']
        resp = es.index(index='products', body=doc , doc_type="_doc", id=doc['_product_id'])
    except Exception as e:
        resp = {"error": str(e)}
    return resp

#search for a product
@app.route(f'/{ELASTIC_PREFIX}/search', methods=['GET'])
def search():
    resp = {}
    try:
        content = request.json
        search_param = content['search_param']
        resp = es.search(index='products', body={"query": {"match": {"description": search_param}}})
    except Exception as e:
        resp = {"error": str(e)}
    return resp  


@app.route(f'/{ELASTIC_PREFIX}/update', methods=['POST'])
def update():
    resp={}
    try:
        content = request.json
        doc = content['product']
        resp = es.update(index='products', body=doc , doc_type="_doc", id=doc['_product_id'])
    except Exception as e:
        resp = {"error": str(e)}
    return resp    

@app.route(f'/{ELASTIC_PREFIX}/delete', methods=['DELETE'])
def delete():
    resp={}
    try:
        content = request.json
        doc = content['product']
        product_id = doc['product_id']
        resp = es.delete(index='products', id=product_id)
    except Exception as e:
        resp = {"error": str(e)}
    return resp


#upload a photo to product s3 bucket
@app.route(f'/{ELASTIC_PREFIX}/upload_photo', methods=['POST'])
def upload_photo():
    resp = {}
    try:
        seller_id = request.form['seller_id']
        product_id = request.form['product_id']
        image = request.files
        upload_product_photo()
    except Exception as e:
        resp = {"error": str(e)}
    return resp