from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Category, Item

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine) 
session = DBSession()

myCategory = Category(name = 'Basketball')
session.add(myCategory)
session.commit()

shoes = Item(name = "Shoes", description = "Made with natural cheese", category = myCategory)
session.add(shoes)
session.commit()