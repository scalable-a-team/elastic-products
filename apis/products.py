from flask import Flask, jsonify, render_template, request, json
from tomlkit import document
from config import *
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from accesskeys.aws_secrets import * #This is hidden from github, but you can use this to store your AWS credentials

app = Flask(__name__)
es = Elasticsearch(
    hosts=ES_HOST,
    http_auth=AWS4Auth(AWSAccessKeyId, AWSSecretKey, 'ap-southeast-1', 'es'), #For signing the request to Elasticsearch
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
    "product_id": 1,
    "supplier_id": 1,
    "description": "This is a test product",
    "price": 1.00,
    "image_url": "https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png"
}

#create product
@app.route(f'/{ELASTIC_PREFIX}/create', methods=['POST'])
def publish():
    """
    Publish product to search engine
    """
    content = request.json
    document = content['product_document']
    print(document)
    resp = es.index(index='products', document = document, id=document['product_id'])
    return jsonify(resp)

#search for a product
@app.route(f'/{ELASTIC_PREFIX}/search', methods=['POST'])
def search():
    content = request.json
    search_param = content['search_param']
    resp = es.search(index='products', body={"query": {"match": {"description": search_param}}})
    return jsonify(resp)


@app.route(f'/{ELASTIC_PREFIX}/update', methods=['POST'])
def update():

    content = request.json
    document = content['product_document']
    resp = es.update(index='products', id=document['product_id'], body={"doc": document})
    return jsonify(resp)    

@app.route(f'/{ELASTIC_PREFIX}/delete', methods=['DELETE'])
def delete():
    content = request.json
    product_id = content['product_id']
    resp = es.delete(index='products', id=product_id)
    return jsonify(resp)

    