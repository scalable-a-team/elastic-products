from flask import Flask, render_template, request, json
from config import *

app = Flask(__name__)

#PRODUCT LISTING CHARACTERISTICS
"""
A product is made up of
product_id: int
supplier_id: int
description: varchar
price: float
image_url: varchar ***maybe an array of varchars, for multiple pictures***
"""

#create product
@app.route(f'/{ELASTIC_PREFIX}/create', methods=['POST'])
def publish():
    """
    Publish product to search engine
    """
    data = request.get_json()
    print(data)
    return json.dumps({'status': 'success'})

#search for a product
@app.route(f'/{ELASTIC_PREFIX}/search', methods=['POST'])
def search():
    ...


@app.route(f'/{ELASTIC_PREFIX}/delete', methods=['DELETE'])
def delete():
    ...

@app.route(f'/{ELASTIC_PREFIX}/update', methods=['POST'])
def update():
    ...
    