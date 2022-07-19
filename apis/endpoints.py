from cgitb import text
from os import write
from flask import Flask, jsonify, request, json
from prod_images import upload_product_photo
from config import *
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from inserts import *
from postdb import Product


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

# ****************************SEARCH ES DATABASE FOR PRODUCT***************************
# SEARCHING FOR A PRODUCT using this method
# the regular params for the search are null,
# The HTTP request needs to contain a "?query=<query>" param in order to search
# otherwise elasticsearch will return no results
# this is meant to pair with the postgres database where all product info is stored
# the mapping of ES -> postgres is just the product_id, which is unique for every product
# use the product id returned by this request to query postgres for the full product listing
@app.route(f'/{ELASTIC_PREFIX}/search/', methods=['GET'])
def search():
    resp = {}
    query = request.args.get('query', default = "")
    try:
        resp = es.search(index='products', body={"query": {"match": {"description": query}}})
    except Exception as e:
        resp = {"error": str(e)}
    return resp  

# **********************DELETE ELASTICSEARCH PRODUCTS************************
# Right now we can delete just one listing if we want to from elasticsearch
# However, this method will be depreciated in the future to work better with postgres
# the delete will happen all in one function and this will no longer be used
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

# **********************GET A PRODUCT FROM POSTGRES DB***********************
# This method will be used to get a product from postgres
# you need to specify the product_id in the request
# the product_id is the primary key for the product in postgres
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

# **********************POST A PRODUCT TO POSTGRES DB***********************
# IMPORTANT INFORMATION !!!!!!!!!!!!!!!!!
# Phtos are uploaded to s3 first, then the urls must be stored in a list
# then passed into the json POST request under 'image_url'
# tags and categories will be pre-made by "staff" and the get_all() method
# needs to be queried to retreive all possible tags and categories for the user to chose
# these need to be in list format as well to properly work with the POST request
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

        image_url = [image for image in images]
        product = create_product(seller_id = seller_id, seller_name = seller_name, product_name = product_name, description= description, price=price, session=session)

        photo_uploads = [create_photo(image, product, session) for image in image_url]
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
    session.close()
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
    tmp = cat.__repr__()
    session.close()
    return tmp




@app.route(f'/{PRODUCT_LISTING_PREFIX}/create/review', methods=['POST'])
def make_new_review():
    session = Session()
    content = request.json
    name = content['name']
    review = content['review']
    stars = int(content['stars'])
    product_id = content['product'] #the id of the product we are leaving review on
    rev = create_review(name, review, stars, session.query(Product).get(product_id), session)
    tmp = rev.__repr__()
    session.close()
    return tmp




@app.route(f'/{PRODUCT_LISTING_PREFIX}/create/tag', methods=['POST'])
def make_new_tag():
    session = Session()
    content = request.json
    tag = content['tag']
    tag_t = create_tag(tag, session)
    tmp =  tag_t.__repr__()
    session.close()
    return tmp



#***********************UPLOAD A PHOTO TO S3 BUCKET***************************
# This method will be used to upload a photo to the s3 bucket
# the returned url will be a publicly accessible url for the photo to be used
# when creating a product listing
# during the product creation, all urls should be cached when the user uploads
# then sent to create_product all together in a list to be added to the product
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
    tmp = {"categories": [cat.__repr__() for cat in lst]}
    session.close()
    return tmp


@app.route(f'/{PRODUCT_LISTING_PREFIX}/tags', methods=['GET'])
def fetch_tags():
    session = Session()
    lst = get_all_tags(session)
    tmp = {"tags": [tag.__repr__() for tag in lst]}
    session.close()
    return tmp

@app.route(f'/{PRODUCT_LISTING_PREFIX}/all_products', methods=['GET'])
def fetch_all_products():
    session = Session()
    lst = get_all_products(session)
    tmp = {"products": [prod.__repr__() for prod in lst]}
    session.close()
    return tmp


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