from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Sport, Base, SportItem

engine = create_engine('sqlite:///sportscatalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()



# soccer
sport1 = Sport(name = "Soccer")

session.add(sport1)
session.commit()


sportItem1 = SportItem(name = "Ball",
                       description = "Ball inflated with air to 9 PSI, usually made of hexagons of fabric.",
                       sport = sport1)

session.add(sportItem1)
session.commit()

sportItem1 = SportItem(name = "Goal",
                       description = "Rectangular goal, with a net.",
                       sport = sport1)

session.add(sportItem1)
session.commit()

sportItem1 = SportItem(name = "Cleats",
                       description = "Shoes with spikes for moving quickly and with traction on a field.",
                       sport = sport1)

session.add(sportItem1)
session.commit()

sportItem1 = SportItem(name = "Shinguards",
                       description = "Pieces of plastic put undernearth socks to protect ones shins from cleats.",
                       sport = sport1)

session.add(sportItem1)
session.commit()

# basketball
sport2 = Sport(name = "Basketball")

session.add(sport2)
session.commit()

sportItem1 = SportItem(name = "Shoes",
                       description = "Shoes designed to provide traction on a wooden court.  Usually designed for ankle support.",
                       sport = sport2)

session.add(sportItem1)
session.commit()

sportItem1 = SportItem(name = "Ball",
                       description = "Generally a leather ball, made to be inflated heavily to bounce on a wooden court.",
                       sport = sport2)

session.add(sportItem1)
session.commit()


# baseball
sport3 = Sport(name = "Baseball")

session.add(sport3)
session.commit()

sportItem1 = SportItem(name = "Ball",
                       description = "Generally a leather ball which is small and durable.  This ball is also heavy which is designed so it can be thrown quickly in the air.",
                       sport = sport3)

session.add(sportItem1)
session.commit()

sportItem1 = SportItem(name = "Bat",
                       description = "Depending on the league in which this baseball is being played.  This bat can be made of metal, wood, or carbon-fiber.",
                       sport = sport3)

session.add(sportItem1)
session.commit()

# frisbee
sport4 = Sport(name = "Frisbee")

session.add(sport4)
session.commit()

sportItem1 = SportItem(name = "Frisbee",
                       description = "A disk of plastic designed to be thrown long distances.",
                       sport = sport4)

session.add(sportItem1)
session.commit()

# Snowboarding
sport5 = Sport(name = "Snowboarding")

session.add(sport5)
session.commit()

sportItem1 = SportItem(name = "Snowboard",
                       description = "A snow which could be made of various materials and shapes for varying skill levels of the rider.  The board is designed to glide on snow such that the rider has the ability to change directions on the way down the hill.",
                       sport = sport5)

session.add(sportItem1)
session.commit()

# Rock Climbing
sport6 = Sport(name = "Rock Climbing")

session.add(sport6)
session.commit()

sportItem1 = SportItem(name = "Harness",
                       description = "A harness is a type of rope that usually goes around a climbers waist.  Harness are generally designed to prevent a climber from falling long distances and injuring themselves.",
                       sport = sport6)

session.add(sportItem1)
session.commit()

sportItem1 = SportItem(name = "Shoes",
                       description = "Rock climbing shoes are designed to be able to grip well on rocks, so the climber does not lose traction and become hurt.",
                       sport = sport6)

session.add(sportItem1)
session.commit()


## Foosball
sport7 = Sport(name = "Foosball")

session.add(sport7)
session.commit()

sportItem1 = SportItem(name = "Table",
                       description = "A table is necessary to play foosball.  The foosball table has multiple poles running through it, and each pole has varying number of players which are used to strike a ball into the goal.",
                       sport = sport7)

session.add(sportItem1)
session.commit()

sportItem1 = SportItem(name = "Ball",
                       description = "A ball or foosball is a very hard ball, used to be shot into the goal.",
                       sport = sport7)

session.add(sportItem1)
session.commit()

## Skating
sport8 = Sport(name = "Skating")

session.add(sport8)
session.commit()

sportItem1 = SportItem(name = "Ice Skates",
                       description = "Shoes with blades attached to them to allow one to maneuver on ice.",
                       sport = sport8)

session.add(sportItem1)
session.commit()

## Hockey
sport9 = Sport(name = "Hockey")

session.add(sport9)
session.commit()

sportItem1 = SportItem(name = "Ice Skates",
                       description = "Shoes with blades attached to them to allow one to maneuver on ice.",
                       sport = sport9)

session.add(sportItem1)
session.commit()

sportItem1 = SportItem(name = "Stick",
                       description = "A stick used control, shoot, and the pass an ice hockey puck.",
                       sport = sport9)

session.add(sportItem1)
session.commit()

sportItem1 = SportItem(name = "Puck",
                       description = "A cylinder of rubber designed to move quickly on ice.",
                       sport = sport9)

session.add(sportItem1)
session.commit()


print "added menu items!"
