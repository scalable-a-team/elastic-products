<h1>All endpoints share the same unique root</h1>

```/api/product/```

#any elasticsearch uses an extra es for all it's services

```/api/product/es```


#POST requests

POST - create a new product

```/api/product/create/product/```

The request should be the following
```json
{
    "product": {
        "product_name": "string",
        "description": "string",
        "price" : "float",
        "tags" : ["Any array of TAG IDS!!! Get tag ids from get tags endpoint"],
        "categories": ["Same as tags, get them from category endpoint"],
        "image_url": ["An array of image urls that you want to attach to product"]
    }
}
```
POST - Create a new category

```/api/product/create/category```

json data should be 
```json
{
    "category": "value"
}
```
POST- Create a new tag

```/api/product/create/tag```

json data should be 
```json
{
    "tag": "value"
}
```

POST - Create a new review

```/api/product/create/review```

json data should be 
```json
{
    "name" : "value",
    "review": "value",
    "stars": "value from 0 - 5",
    "product" : "product_id the person is leaving the review on"
}
```


POST - upload a photo

***Use Form data, not json***

```/api/product/create/photo```

```files["image"] = photo```
returns the url of the photos location on s3


#Get requests


GET - search ES for a product

```/api/product/es/search?query=&from=&size```

query: the users query, default is none

from: the index to load results from e.g. when going 
to next page, default is 0

size: the amount of results to load, default is 10


GET - lists all categories
```/api/product/categories```

GET - lists all tags
```/api/product/tags```

GET - lists all products ***this response could be very large***
```/api/product/all_products```

#Delete request

DELETE - product with id
```/api/product/delete/<id>```

DELETE - product with id from Elastic
```/api/product/es/delete/<id>```


***THESE METHODS WILL NUKE THE DATABASES AND REQUIRE A RESTART OF PRODUCT SERVICE***

DELETE - all products from postgres
```/api/product/delete/all```

DELETE - all products from elasticsearch
```/api/product/es/delete/all```