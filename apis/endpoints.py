from cgitb import text
from os import write
from flask import Flask, jsonify, request, json
from prod_images import upload_product_photo
from config import *
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from inserts import *


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
@app.route(f'/{ELASTIC_PREFIX}/search/', methods=['GET'])
def search():
    resp = {}
    query = request.args.get('query', default = "")
    try:
        resp = es.search(index='products', body={"query": {"match": {"description": query}}})
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

from base import Session


@app.route(f'/{PRODUCT_LISTING_PREFIX}/<id>', methods=['GET'])
def fetch_product(id):
    session = Session()
    resp = {}
    id = int(id)
    try:
        resp = get_product(id, session).__repr__()
    except Exception as e:
        resp = {"error": str(e)}
    session.close()
    return resp

#publish a product to mongodb using sqalchemy
@app.route(f'/{PRODUCT_LISTING_PREFIX}/create/product', methods=['POST'])
def publish_product():
    session = Session()
    resp = {}
    try:
        content = request.json
        product = content['product']

        seller_name = product['seller_name']
        seller_id = int(product['seller_id'])
        product_name = product['product_name']
        description = product['description']
        price = float(product['price'])

        images = product['image_url'] #should be a list of urls
        print(type(images))

        image_url = [image for image in images]
        product = create_product(seller_id = seller_id, seller_name = seller_name, product_name = product_name, description= description, price=price, session=session)

        photo_uploads = [create_photo(image, product) for image in image_url]
        elastic_response = publish_product_elastic(
            product_id = product._id,
            seller_id = product._seller_id,
            product_name = product.product_name,
            description = product.description,
            price = product.price
        )
        resp = {"product": product.__repr__(), "photo_uploads": [photo.__repr__() for photo in photo_uploads], 
                "es_service": elastic_response}
    except Exception as e:
        resp = {"error": str(e)}
    return resp

def publish_product_elastic(product_id, seller_id, product_name, description, price):
    doc = jsonify({
        "_product_id": product_id,
        "_supplier_id": seller_id,
        "product_name": product_name,
        "description": description,
        "price": price
    })

    resp = es.index(index='products', body=doc , doc_type="_doc", id=product_id)
    return resp

@app.route(f'/{PRODUCT_LISTING_PREFIX}/create/category', methods=['POST'])
def make_new_category():
    session = Session()
    content = request.json
    category = content['category']
    cat = create_category(category, session)
    session.close()
    return cat.__repr__()

@app.route(f'/{PRODUCT_LISTING_PREFIX}/create/review', methods=['POST'])
def make_new_review():
    session = Session()
    content = request.json
    name = content['name']
    review = content['review']
    stars = int(content['stars'])
    product = content['product'] #the id of the product we are leaving review on
    rev = create_review(name, review, stars)
    return rev.__repr__()

@app.route(f'/{PRODUCT_LISTING_PREFIX}/create/tag', methods=['POST'])
def make_new_tag():
    session = Session()
    content = request.json
    tag = content['tag']
    tag_t = create_tag(tag, session)
    return tag_t.__repr__()

#upload a photo to product s3 bucket
@app.route(f'/{PRODUCT_LISTING_PREFIX}/upload_photo', methods=['POST'])
def upload_photo():
    resp = {}
    try:
        seller_id = request.form['seller_id']
        product_id = request.form['product_id']
        image = request.files['image']
        s3_url = upload_product_photo(product_id, seller_id, image) #gets the s3 public url
        resp = {"s3_url": s3_url}
    except Exception as e:
        resp = {"error": str(e)}
    return resp


@app.route(f'/{PRODUCT_LISTING_PREFIX}/categories', methods=['GET'])
def fetch_categories():
    session = Session()
    lst = get_all_categories(session)
    session.close()
    return {"categories": [cat.__repr__() for cat in lst]}


@app.route(f'/{PRODUCT_LISTING_PREFIX}/tags', methods=['GET'])
def fetch_tags():
    session = Session()
    lst = get_all_tags(session)
    session.close()
    return {"tags": [tag.__repr__() for tag in lst]}

@app.route(f'/{PRODUCT_LISTING_PREFIX}/all_products', methods=['GET'])
def fetch_all_products():
    session = Session(session)
    lst = get_all_products()
    session.close()

    return {"products": [prod.__repr__() for prod in lst]}


#since we delete database need to clear elasticsearch too
@app.route(f'/admin/delete/database/all', methods=['DELETE'])
def delete_database():
    session = Session()
    resp = {}
    try:
        RIP_METHOD(session)
        
        resp = {"message": "database deleted"}
    except Exception as e:
        resp = {"error": str(e)}

    session.close()
    return resp

@app.route(f'/admin/delete/elasticsearch/all', methods=['DELETE'])
def delete_elasticsearch():
    resp = {}
    try:
        es.delete_by_query(index='products', body={"query": {"match_all": {}}})
        resp = {"message": "elasticsearch deleted"}
    except Exception as e:
        resp = {"error": str(e)}
    return resp