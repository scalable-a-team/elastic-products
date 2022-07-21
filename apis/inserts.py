from base import Session, Engine, Base
from postdb import Product, Image, Review, Tag, Category

Base.metadata.create_all(Engine)


def create_product(
    seller_id = 1, 
    seller_name="John Doe", 
    product_name="Default Product", 
    description="Default Description", 
    price=0.0, tags = [], 
    categories = [],
    session = None):

    product = Product(seller_id, seller_name, product_name, description, price)
    product.tags = [(session.query(Tag).get(tag)) for tag in tags]
    product.categories = [(session.query(Category).get(category)) for category in categories]
    # product.categories = categories
    product_to_db(product, session)
    return product

def create_photo(image_url, product, session):
    image = Image(image_url)
    image.product = product
    image_to_db(image, session)
    return image

def create_tag(tag_name, session):
    tag = Tag(tag_name)
    tag_to_db(tag, session)
    return tag

def create_category(category_name, session):
    category = Category(category_name)
    category_to_db(category, session)
    return category

def create_review(customer_name="John Doe", 
        review_text="Default Review", 
        stars=5, 
        product=None,
        session = None):
    review = Review(customer_name, review_text, stars, product)
    review.product = product
    review_to_db(review, session)
    return review



def product_to_db(product, session):

    session.add(product)
    session.commit()
    
    return product

def image_to_db(image, session):

    session.add(image)
    session.commit()
    
    return image

def review_to_db(review, session):
    
    session.add(review)
    session.commit()
    
    return review

def tag_to_db(tag, session):
    
    session.add(tag)
    session.commit()
    
    return tag

def category_to_db(category, session):
    
    session.add(category)
    session.commit()
    
    return category


def get_product(id, session):
    resp = {}
    try:
        resp = session.query(Product).get(id)
    except Exception as e:
        resp = {"error": str(e)}

    return resp


def get_all_product_by_seller(seller_id, session, size, page):
    resp = {}
    try:
        resp = session.query(Product).filter(Product._seller_id == seller_id).offset((page-1)*size).limit(size)
    except Exception as e:
        resp = {"error": str(e)}

    return resp


def get_all_product_by_seller_count(seller_id, session):
    resp = {}
    try:
        resp = session.query(Product).filter(Product._seller_id == seller_id).count()
    except Exception as e:
        resp = {"error": str(e)}

    return resp

def get_all_products(session):
    resp = {}
    try:
        resp = session.query(Product).all()
    except Exception as e:
        resp = {"error": str(e)}

    return resp

def get_all_categories(session):
    resp = {}
    try:
        resp = session.query(Category).all()
    except Exception as e:
        resp = {"error": str(e)}
    return resp

def get_all_tags(session):
    resp = {}
    try:
        resp = session.query(Tag).all()
    except Exception as e:
        resp = {"error": str(e)}
    return resp


#**************************ADMIN UTILITIES********************************

#this will nuke the database and requires a restart of the application to relbuild it
def RIP_METHOD():

    Base.metadata.drop_all(Engine)

    return True