from base import Session, Engine, Base
from postdb import Product, Image, Review, Tag, Category

Base.metadata.create_all(Engine)


def create_product(
    seller_id = 1, 
    seller_name="John Doe", 
    product_name="Default Product", 
    description="Default Description", 
    price=0.0, tags = [], 
    categories = []):

    session = Session()
    product = Product(seller_id, seller_name, product_name, description, price)
    [product.add_tag(session.query(Tag).get(tag)) for tag in tags]
    # product.categories = categories
    product_to_db(product, session)
    session.close()
    return product

def create_photo(image_url, product):
    session = Session()
    image = Image(image_url)
    image.product = product
    image_to_db(image, session)
    session.close()
    return image

def create_tag(tag_name):
    session = Session()
    tag = Tag(tag_name)
    tag_to_db(tag, session)
    session.close()
    return tag

def create_category(category_name):
    session = Session()
    category = Category(category_name)
    category_to_db(category, session)
    session.close()
    return category

def create_review(customer_name="John Doe", 
        review_text="Default Review", 
        stars=5, 
        product=None):
    session = Session()
    review = Review(customer_name, review_text, stars)
    review.product = product
    review_to_db(review, session)
    session.close()
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


def get_product(id):
    session = Session()
    resp = {}
    try:
        resp = session.query(Product).get(id)
    except Exception as e:
        resp = {"error": str(e)}

    session.close()
    return resp

def get_all_products():
    session = Session()
    resp = {}
    try:
        resp = session.query(Product).all()
    except Exception as e:
        resp = {"error": str(e)}

    session.close()
    return resp

def get_all_categories():
    resp = {}
    session = Session()
    try:
        resp = session.query(Category).all()
    except Exception as e:
        resp = {"error": str(e)}
    session.close()
    return resp

def get_all_tags():
    resp = {}
    session = Session()
    try:
        resp = session.query(Tag).all()
    except Exception as e:
        resp = {"error": str(e)}
    session.close()
    return resp


#**************************ADMIN UTILITIES********************************

def RIP_METHOD():
    session = Session()
    session.query(Image).delete()
    session.query(Category).delete()
    session.query(Tag).delete()
    session.query(Review).delete()
    session.query(Product).delete()
    session.commit()
    session.close()
    return True