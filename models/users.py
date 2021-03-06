from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from database import Base # should be executed at the root package

class Users(Base):
    # class attr
    # create a Table in database
    __tablename__ = 'users'
    
    id = Column(String, primary_key=True)
    nick_name = Column(String)
    image_url = Column(String(length=256))
    created_time = Column(DateTime, default=func.now())

    orders = relationship('Orders', backref='user') # relationship(cls_name, backref='var_name')
    # user.orders
    # order.user, for backref
    
    """ # instance attr
    # without init, one could use argument to modify the class attr. ex. Users(id='123')
    def __init__(self, name=None, email=None):
        self.name = name
        self.email = email"""
    
    # print an instance
    def __repr__(self):
        return f'<User {self.nick_name!r}>'


""" print(Users().query.all())
print(Users().query.session)
a = Users()
print(a)
print(a.i, a.id, a.nick_name)
a = Users(i = 345, id=456)
print(a.i, a.id, a.nick_name)
print(a.query.all()) """