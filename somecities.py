from database_setup import User, Base, Place, City
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
engine = create_engine('sqlite:///citiescatalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create dummy user
user1 = User(name="Jhon Doe", email="jhondoe@demo.com",
             picture='https://imgplaceholder.com/150x150')
session.add(user1)
session.commit()

city1 = City(name="Kansas City", user=user1)

session.add(city1)
session.commit()

place1 = Place(name="Victoria", description="Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Curabitur",city=city1, user=user1)

session.add(place1)
session.commit()

print('Finished populating the database!')
