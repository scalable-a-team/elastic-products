import decimal
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
    query = str(request.args.get('query', default = ""))
    after = int(request.args.get('after', default = 0))
    suggest_size = int(request.args.get('suggest_size', default = 10))

    try:

        if query == "":
            resp = es.search(index="products", 
            body={'query': {"match_all": {}}})
        else:
            resp = es.search(index='products', body={
                "query" : { 'match' : { 'searchable': query } },
                "search_after" : [after],
                "size": suggest_size,
                },
                sort= "_product_id"
                )

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
        seller_id = request.headers['X-Kong-Jwt-Claim-Userid']
        first_name = request.headers['X-Kong-Jwt-Claim-Firstname']
        last_name = request.headers['X-Kong-Jwt-Claim-Lastname']
        seller_name = f"{first_name} {last_name}"
        product_name = product['product_name']
        description = product['description']
        price = decimal.Decimal(product['price'])
        tags = product['tags'] #id's of tags, will be queried later
        categories = product['categories']#same as tags, use cat id

        images = product['image_url'] #should be a list of urls

        image_url = [image for image in images]
        product = create_product(
            seller_id = seller_id, 
            seller_name = seller_name, 
            product_name = product_name, 
            description= description, 
            price=price,
            tags = tags,
            categories = categories,
            session = session)

        photo_uploads = [create_photo(image, product, session) for image in image_url]
        es_resp = {}
        try:
            es_resp = publish_product_elastic(
                product_id = int(product._id),
                product_name = str(product.product_name),
                description = str(product.description),
                price = float(product.price),
                tags = ",".join([tag.__repr__()["tag_name"] for tag in product.tags]),
                categories = ",".join([cat.__repr__()["category_name"] for cat in product.categories]),
            )
        except Exception as e:
            es_resp = {"error": str(e)}
        resp = {"product": product.__repr__(), "photo_uploads": [photo.__repr__() for photo in photo_uploads], 
                "es_service": es_resp}
    except Exception as e:
        resp = {"error": str(e)}
    session.close()
    return jsonify(resp)


# THIS METHOD IS FOR USE WHEN THE ELASTIC SEARCH PART OF THE PRODUCT CREATION FAILS
# THIS METHOD IS CALLED DIRECTLY FROM PRODUCT CREATION, BUT CAN BE RECREATED IF
# IT FAILS THE FIRST TIME
@app.route(f'/{ELASTIC_PREFIX}/create/product', methods=['POST'])
def create_product_elastic():
    resp = {}
    try:
        content = request.json
        product = content['product']

        product_id = int(product['product_id'])
        product_name = product['product_name']
        description = product['description']
        price = float(product['price'])
        tags = product['tags']
        categories = product['categories']
        resp = publish_product_elastic(product_id, product_name, description, price, tags, categories)
    except Exception as e:
        resp = {"error": str(e)}
    return resp

# @app.route(f"/{ELASTIC_PREFIX}/repair", methods=["PATCH"])
# def repair_es():
#     resp = {}
#     session = Session()
#     try:
#         products = session.query(Product).all()
#         for product in products:
#             #check if product id made it into elasticsearch
#             es_resp = es.get(index='_products_id', id=product._id)
#             print(es_resp)
#     except Exception as e:
#         resp = {"error": str(e)}
#     return resp

def publish_product_elastic(product_id, product_name, description, price, tags, categories):
    doc = {
        "_product_id": product_id,
        "product_name": product_name,
        "description": description,
        "price": price,
        "searchable": f'{product_name} {tags} {categories} {description}',
    }

    resp = es.index(index='products', body=doc, doc_type="_doc", id=product_id)
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
        seller_id = request.headers['X-Kong-Jwt-Claim-Userid']
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
@app.route(f'/{PRODUCT_LISTING_PREFIX}/delete/database/all', methods=['DELETE'])
def delete_database():

    resp = {}
    try:
        reply = RIP_METHOD()
        resp = {"message": reply}
    except Exception as e:
        resp = {"error": str(e)}
    return resp

@app.route(f'/{PRODUCT_LISTING_PREFIX}/admin/delete/elasticsearch/all', methods=['DELETE'])
def delete_elasticsearch():
    resp = {}
    try:
        es.delete_by_query(index='products', body={"query": {"match_all": {}}})
        resp = {"message": "elasticsearch deleted"}
    except Exception as e:
        resp = {"error": str(e)}
    return resp

@app.route(f'/{PRODUCT_LISTING_PREFIX}/admin/delete/product/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    resp = []
    try:
        session = Session()
        product = session.query(Product).get(product_id)
        product_id = int(product._id)
        resp.append(session.delete(product))
        session.commit()
        session.close()
        resp.append(es.delete(index='products', id=product_id))
    except Exception as e:
        resp = {"error": str(e)}
    return {'delete request' : resp }