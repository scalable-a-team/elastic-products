from cgitb import text
from os import write
from flask import Flask, jsonify, request, json
from prod_images import upload_product_photo
from config import *
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from accesskeys.aws_secrets import * 
import sqlalchemy as db
from sqlalchemy import Table, Column, Integer, String, DateTime, ForeignKey, Boolean, Float, Text, MetaData

app = Flask(__name__)
es = Elasticsearch(
    hosts=ES_HOST,
    http_auth=AWS4Auth(AWS_ACCESS_KEY_ID, AWS_SECRET_KEY, 'ap-southeast-1', 'es'), #For signing the request to Elasticsearch
    verify_certs=True,
    use_ssl=True,
    connection_class=RequestsHttpConnection,
    port=443
)

engine = db.create_engine(POSTGRES_DATABASE)

#PRODUCT LISTING CHARACTERISTICS
"""
A product is made up of
product_id: int
supplier_id: int
description: varchar
price: float
image_url: varchar ***maybe an array of varchars, for multiple pictures***
"""

example_product = { #this will just be the main info that is cached in ES
    "_product_id": 1, #hidden
    "_supplier_id": 1, #hidden
    "product_name": "Google Logo",
    "description": "This is a test product, the description is here",
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
        print(search_param)
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
        image = request.files['image']
        resp = upload_product_photo(product_id, seller_id, image)
    except Exception as e:
        resp = {"error": str(e)}
    return resp

#just use this the first time the database needs to be created, not to really be used in prod
@app.route(f'/{PRODUCT_LISTING_PREFIX}/create_db_table', methods=['POST'])
def create_db_table():
    resp = {}
    try:
        sql = text("CREATE TABLE IF NOT EXISTS products (\
            _product_id INTEGER PRIMARY KEY,\
            _supplier_id INTEGER,\
            seller_name VARCHAR NOT NULL,\
            product_name VARCHAR NOT NULL,\
            description VARCHAR,\
            price FLOAT NOT NULL,\
            images text[],\
            reviews text[],\
            tags text[],\
            category VARCHAR NOT NULL,\
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,\
        );")
        engine.execute(sql)
        resp = {"success": "true"}
    except Exception as e:
        resp = {"error": str(e)}
    return resp


#product class for the product listing
class Product:
    def __init__(self, product_id, supplier_id, seller_name, product_name, description, price, images, reviews, tags, category, created_at):
        self.tablename = "products"
        self.product_id = product_id
        self.supplier_id = supplier_id
        self.seller_name = seller_name
        self.product_name = product_name
        self.description = description
        self.price = price
        self.images = images
        self.reviews = reviews
        self.tags = tags
        self.category = category
        self.created_at = created_at
    def __repr__(self):
        return f"Product({self.product_id}, {self.supplier_id}, {self.seller_name}, {self.product_name}, {self.description}, {self.price}, {self.images}, {self.reviews}, {self.tags}, {self.category}, {self.created_at})"
    def __str__(self):
        return f"Product({self.product_id}, {self.supplier_id}, {self.seller_name}, {self.product_name}, {self.description}, {self.price}, {self.images}, {self.reviews}, {self.tags}, {self.category}, {self.created_at})"
    def __eq__(self, other):
        return self.product_id == other.product_id
    def __hash__(self):
        return hash(self.product_id)
    def __lt__(self, other):
        return self.product_id < other.product_id
    def __le__(self, other):
        return self.product_id <= other.product_id
    def __gt__(self, other):
        return self.product_id > other.product_id
    def __ge__(self, other):
        return self.product_id >= other.product_id
    def __ne__(self, other):
        return self.product_id != other.product_id

class Reviews:
    def __init__(**args):
        return "Not yet implemented"
class Tags:
    def __init__(**args):
        return "Not yet implemented"
class Categories:
    def __init__(**args):
        return "Not yet implemented"

#publish a product to mongodb using sqalchemy
@app.route(f'/{PRODUCT_LISTING_PREFIX}/publish', methods=['POST'])
def publish_product():
    with engine.connect() as conn:
        try:
            content = request.json
            product = content['product']

            product_id = product['product_id']
            seller_id = product['seller_id']
            seller_name = product['seller_name']
            product_name = product['product_name']
            description = product['description']
            price = product['price']
            images = product['images']
            reviews = product['reviews']
            tags = product['tags']
            categories = product['categories']

            conn.execute(text(f"INSERT INTO products (_product_id, _supplier_id, seller_name, product_name, description, \
            price, images, reviews, tags, categories) VALUES ({product_id}, {seller_id}, '{seller_name}', '{product_name}', \
                '{description}', {price}, '{images}', '{reviews}', '{tags}', '{categories}')"))
        except Exception as e:
            return {"error": str(e)}

product_full = {
    "_product_id": "",
    "_supplier_id": "",
    "seller name": "",
    "product_name": "",
    "description": "",
    "price": 0.00,
    "images": [],
    "reviews": [],
    "tags": [],
    "categories": [],
}

@app.route(f'/{PRODUCT_LISTING_PREFIX}/listing/<product_id>', methods=['GET'])
def get_product_page(product_id):
    ...