from sqlalchemy import Column, Numeric, String, Integer, ForeignKey, DateTime, Boolean, Float, Text, MetaData, Table
from sqlalchemy.orm import relationship
from base import Base

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
    _seller_id = Column(Integer)
    seller_name = Column(String)
    product_name = Column(String)
    description = Column(String)
    price = Column(Numeric)
    created_at = Column(DateTime)

    tags = relationship("Tag", secondary=tag_to_product_association)
    categories = relationship("Category", secondary=cat_to_product_association)
    def __init__(self, seller_name, product_name, description, price, image_url):
        self.seller_name = seller_name
        self.product_name = product_name
        self.description = description
        self.price = price
        self.image_url = image_url

#*******************************************IMAGES**********************************************************
#One to many relationship, products has many images
class Image(Base):
    __tablename__ = 'images'
    _id = Column(Integer, primary_key=True)
    _product_id = Column(Integer, ForeignKey('products._id'))
    image_url = Column(String)
    product = relationship("Product", backref="products")
    def __init__(self, image_url):
        self.image_url = image_url

#*******************************************REVIEWS**********************************************************
#one to many relationship, products has many reviews
class Review(Base):
    __tablename__ = 'reviews'
    _id = Column(Integer, primary_key=True)
    _product_id = Column(Integer, ForeignKey('products._id'))
    customer_name = Column(String)
    review_text = Column(String)
    stars = Column(Integer)

#*******************************************TAGS**********************************************************

#many to many relationship, each tag can contain many products and vice versa
class Tag(Base):
    __tablename__ = 'tags'
    _id = Column(Integer, primary_key=True)
    tag_name = Column(String)


#*******************************************CATEGORIES**********************************************************

#many to many, each category has many relationships with products
class Category(Base):
    __tablename__ = 'categories'
    _id = Column(Integer, primary_key=True)
    category_name = Column(String)

