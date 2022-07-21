from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Numeric, String, Integer, ForeignKey, DateTime, Boolean, Float, Text, MetaData, Table
from sqlalchemy.orm import relationship
from base import Base
from flask import jsonify
import datetime as dt

tag_to_product_association = Table('product_tags', Base.metadata,
    Column('product_id', Integer, ForeignKey('products._id')),
    Column('tag_id', Integer, ForeignKey('tags._id'))
)

cat_to_product_association = Table('product_categories', Base.metadata,
    Column('product_id', Integer, ForeignKey('products._id')),
    Column('category_id', Integer, ForeignKey('categories._id'))
)

class Product(Base):
    __tablename__ = 'products'
    _id = Column(Integer, primary_key=True)
    _seller_id = Column(UUID(as_uuid=True))
    seller_name = Column(String)
    product_name = Column(String)
    description = Column(String)
    price = Column(Numeric(precision=12, scale=2))
    created_at = Column(DateTime)

    tags = relationship("Tag", secondary=tag_to_product_association)
    categories = relationship("Category", secondary=cat_to_product_association)

    def __init__(self, seller_id, seller_name, product_name, description, price):
        self._seller_id = seller_id
        self.seller_name = seller_name
        self.product_name = product_name
        self.description = description
        self.price = price
        self.created_at = dt.datetime.utcnow()
    
    def __repr__(self):
        return {
            '_id': self._id,
            'seller_id': self._seller_id,
            'seller_name': self.seller_name,
            'product_name': self.product_name,
            'description': self.description,
            'price': self.price,
            'created_at': self.created_at,
            'tags': [tag.tag_name for tag in self.tags],
            'categories': [category.category_name for category in self.categories],
            'reviews': [review.__repr__() for review in self.reviews],
            'images': [image.image_url for image in self.images]
        }
        
    def add_tag(self, tag):
        self.tags.append(tag)
        return self

    def add_category(self, category):
        self.categories.append(category)
        return self
        

#*******************************************IMAGES**********************************************************
#One to many relationship, products has many images
class Image(Base):
    __tablename__ = 'images'
    _id = Column(Integer, primary_key=True)
    _product_id = Column(Integer, ForeignKey('products._id'))
    image_url = Column(String)
    product = relationship("Product", backref="images")
    def __init__(self, image_url):
        self.image_url = image_url
    
    def __repr__(self):
        return {
            '_id': self._id,
            'product_id': self._product_id,
            'image_url': self.image_url
        }

#*******************************************REVIEWS**********************************************************
#one to many relationship, products has many reviews
class Review(Base):
    __tablename__ = 'reviews'
    _id = Column(Integer, primary_key=True)
    _product_id = Column(Integer, ForeignKey('products._id'))
    customer_name = Column(String)
    review_text = Column(String)
    stars = Column(Integer)
    product = relationship("Product", backref="reviews")
    def __init__(self, customer_name, review_text, stars, product):
        self.customer_name = customer_name
        self.review_text = review_text
        self.stars = stars
        self.product = product
    def __repr__(self) -> str:
        return {
            'customer_name': self.customer_name,
            'review_text': self.review_text,
            'stars': self.stars,
        }

#*******************************************TAGS**********************************************************

#many to many relationship, each tag can contain many products and vice versa
class Tag(Base):
    __tablename__ = 'tags'
    _id = Column(Integer, primary_key=True)
    tag_name = Column(String)
    def __init__(self, tag_name):
        self.tag_name = tag_name

    def __repr__(self):
        return {
            '_id': self._id,
            'tag_name': self.tag_name
        }
        


#*******************************************CATEGORIES**********************************************************

#many to many, each category has many relationships with products
class Category(Base):
    __tablename__ = 'categories'
    _id = Column(Integer, primary_key=True)
    category_name = Column(String)
    def __init__(self, category_name):
        self.category_name = category_name

    def __repr__(self):
        return {
            '_id': self._id,
            'category_name': self.category_name
        }

