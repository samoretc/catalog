from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Category, Item

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine) 
session = DBSession()

basketball = Category(name = 'Basketball')
session.add(basketball)
session.commit()

shoes = Item(name = "Kobe Shoes", category =  basketball, image_url =  "http://www.kobebryantshoes.com/shoes/images/nike_hyperdunk_lakers_04.jpg")
session.add(shoes)
session.commit()

ball = Item(name = "Ball", category = basketball, image_url = "https://upload.wikimedia.org/wikipedia/commons/7/7a/Basketball.png")
session.add(ball)
session.commit()

tennis = Category(name = 'Tennis')
session.add(tennis)
session.commit()

racquet = Item(name = "Racket" ,  category = tennis, image_url= "http://static.giantbomb.com/uploads/scale_small/0/140/376641-tennis_racket.jpg")
session.add(racquet)
session.commit()

soccer = Category(name = 'Soccer')
session.add(soccer)
session.commit()

soccerball = Item(name = "Soccer Ball", category = soccer, image_url = "http://assets.academy.com/mgen/08/10327808.jpg")
session.add(soccerball)
session.commit()

print 'added categories with a few items'