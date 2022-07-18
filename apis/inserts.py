from numpy import product
from requests import session
from base import Session, Engine, Base
from postdb import Product, Image, Review, Tag, Category

Base.metadata.create_all(Engine)

def create_product(seller_name="John Doe", product_name="Default Product", description="Default Description", price=0.0, tags = [], categories = []):
    product = Product(seller_name, product_name, description, price)
    product.tags = [create_tag(tag) for tag in tags]
    product.categories = [create_category(category) for category in categories]
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
    session = Session()
    session.add(product)
    session.commit()
    session.close()
    return product

def image_to_db(image):
    session = Session()
    session.add(image)
    session.commit()
    session.close()
    return image

def review_to_db(review):
    session = Session()
    session.add(review)
    session.commit()
    session.close()
    return review

def tag_to_db(tag):
    session = Session()
    session.add(tag)
    session.commit()
    session.close()
    return tag

def category_to_db(category):
    session = Session()
    session.add(category)
    session.commit()
    session.close()
    return category