from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base() # i'm not quite sure what a base is. 

# class User(Base):
# 	__tablename__ = 'user'
# 	id = Column
class User(Base): 
	__tablename__ = 'user'
	
	id = Column(Integer, primary_key = True)
	name = Column(String(250), nullable=False)
	email = Column(String(250), nullable=False)
	picture = Column(String(250))

class Category(Base): 
	__tablename__ = 'category'

	id = Column(Integer , primary_key = True)
	name = Column(String(250), nullable=False)
	
	

class Item(Base): 
	__tablename__ = 'item'

	id = Column(Integer, primary_key = True) 
	name = Column(String(250))
	image_url = Column(String(250))
	category_id = Column(Integer, ForeignKey('category.id')) # tablename.column
	category = relationship(Category)	## I'm not quite sure the purpose of relationship, and what is the difference between the child and the parent

	user_id = Column(Integer , ForeignKey('user.id'))
	user = relationship(User)

	@property
	def serialize(self):
		return { 'name': self.name, 'image_url': self.image_url}




engine = create_engine('sqlite:///catalog.db') ### creates the database 


Base.metadata.create_all(engine)
