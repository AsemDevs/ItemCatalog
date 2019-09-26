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

city1 = City(name="Mecca", user=user1)

session.add(city1)
session.commit()

place1 = Place(name="Grand Mosque (Haram)", description="The grand mosque of Makkah commonly known as Masjid al-Haram is the largest mosque in the world surrounded by the holiest places of Islam. Muslims around the world pray in the direction of Grand Mosque, 5 times a day",city=city1, user=user1)

session.add(place1)
session.commit()

city2 = City(name="Cairo", user=user1)

session.add(city2)
session.commit()

place21 = Place(name="Al-Azhar Mosque", description="Al-Azhar Mosque is the finest building of Cairo's Fatimid era and one of the city's earliest surviving mosques, completed in AD 972.",city=city2, user=user1)
place22= Place(name="The Egyptian Museum", description="The absolutely staggering collection of antiquities displayed in Cairo's Egyptian Museum makes it one of the world's great museums. You would need a lifetime to see everything on show.",city=city2, user=user1)

session.add(place21)
session.add(place22)

session.commit()

city3 = City(name="Dubai", user=user1)

session.add(city3)
session.commit()

place3 = Place(name="Burj Khalifa", description="Dubai's landmark building is the Burj Khalifa, which at 829.8 meters is the tallest building in the world and the most famous of the city's points of interest",city=city3, user=user1)

session.add(place3)
session.commit()

print('Finished populating the database!')
