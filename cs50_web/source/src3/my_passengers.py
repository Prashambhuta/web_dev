#!usr/bin/env python3

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine('postgresql:///flights')
db = scoped_session(sessionmaker(bind=engine))

def main():

    # List all flights
    flights = db.execute("SELECT * FROM flights").fetchall()
    for flight in flights:
        print("Flights no: %d from %s to %s of %d minutes duration." % (flight.id, flight.origin, flight.destination, flight.duration))

    # Ask for user input
    flight_id = int(input("\nSelect flight: "))
    passengers = db.execute("SELECT name, origin, destination FROM flights FULL OUTER JOIN passengers ON passengers.flight_id = flights.id WHERE flight_id = %d" % flight_id).fetchall()
    # print("Passengers: %s" % passengers.name)
    if passengers == []:
        print("No passengers.")
    else:
        for passenger in passengers:
            print("Passenger on flight_id: %d is %s" % (flight_id,passenger.name))




if __name__ == "__main__":
    main()