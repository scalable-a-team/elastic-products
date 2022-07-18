from numpy import product
from requests import session
from base import Session, Engine, Base
from postdb import Product, Image, Review, Tag, Category

Base.metadata.create_all(Engine)
session = Session()

def create_product(seller_id = 1, seller_name="John Doe", product_name="Default Product", description="Default Description", price=0.0, tags = [], categories = []):
    product = Product(seller_id, seller_name, product_name, description, price)
    [product.add_tag(session.query(Tag).get(tag)) for tag in tags]
    # product.categories = categories
    product_to_db(product)
    return product

def create_photo(image_url, product):
    image = Image(image_url)
    image.product = product
    image_to_db(image)
    return image

def create_tag(tag_name):
    tag = Tag(tag_name)
    tag_to_db(tag)
    return tag

def create_category(category_name):
    category = Category(category_name)
    category_to_db(category)
    return category

def create_review(customer_name="John Doe", review_text="Default Review", stars=0, product=None):
    review = Review(customer_name, review_text, stars)
    review.product = product
    review_to_db(review)
    return review



def product_to_db(product):

    session.add(product)
    session.commit()
    
    return product

def image_to_db(image):

    session.add(image)
    session.commit()
    
    return image

def review_to_db(review):
    
    session.add(review)
    session.commit()
    
    return review

def tag_to_db(tag):
    
    session.add(tag)
    session.commit()
    
    return tag

def category_to_db(category):
    
    session.add(category)
    session.commit()
    
    return category