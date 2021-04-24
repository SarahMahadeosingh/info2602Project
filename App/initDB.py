from main import app
from models import db , Room , User , Customer
from sqlalchemy.exc import IntegrityError

import csv

global data

db.create_all(app=app)


 

#for x in range (0,11):
#  room = Room(type="King" , roomRate=250.00 , roomNumber=x);

# add code to parse csv, create and save room objects
with open("App/rooms.csv", "r") as csv_file:
  data = csv.DictReader(csv_file)

  for row in data:
    room= Room(roomType=row["type"], roomRate= row["roomRate"], roomNumber= row["roomNumber"])

    try:
      db.session.add(room)
      db.session.commit() 
  
    except IntegrityError:
        db.session.rollback()
        print("Room Already Exists")

  print("Database Initialized!")

#Sirs Login

try:
    
  user = User( email="bob@gmail.com")
  user.set_password("bobpass")
  customer= Customer(email= "bob@gmail.com", firstName="bob", lastName= "builder", phoneNumber= 1234567, country="Trinidad", address="Home")
  db.session.add(user)
  db.session.add(customer)
  db.session.commit()

except IntegrityError:
    db.session.rollback()

print("Bob Added!")