from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
db = SQLAlchemy()
import datetime
import random
#Email was used as the primary key for Users & Email was the ForeignKey in other Classes

#Web_Users was changed to Users, because SQL had issues identifying the table with an underscore for db.relationship

class User(UserMixin, db.Model):
  id= db.Column(db.Integer, unique= True, default= random.randint(1, 100000000) )
  email= db.Column('email', db.String(120), nullable=False, primary_key=True)
  password= db.Column('password', db.String(120), nullable= False)
  customer= db.relationship("Customer", backref="user", lazy= True, uselist= False)
  bookings= db.relationship("Booking", backref="user", lazy= True)
  bills = db.relationship("Bill", backref="user", lazy= True)

  def set_password(self, password):
    self.password= generate_password_hash(password, method="sha256")

  def check_password(self, password):
    return check_password_hash(self.password, password)

  def toDict(self):             #Missing bills...should i include a toDict() ?
    return {
        'id': self.id,
        'customer': self.customer.toDict(),
        'email': self.email,
        'bookings': [ booking.toDict() for booking in self.bookings],
        'bills': [bill.toDict() for bill in self.bills] 
    }
    
  

#can be made compulsory for final edits
class Customer(db.Model):
  email= db.Column('email', db.String(120), db.ForeignKey("user.email"), primary_key=True)
  firstName = db.Column('firstName', db.String(50))
  lastName =  db.Column('lastName', db.String(50))
  phoneNumber = db.Column('phoneNumber', db.Integer)
  country = db.Column('country', db.String(120))
  address= db.Column('address', db.String(120))


  def toDict(self):
    return{
            'email': self.email,
            'firstName': self.firstName,
            'lastName': self.lastName,
            'phoneNumber': str(self.phoneNumber),
            'country': self.country,
            'address':self.address
        }




class Room(db.Model):
  roomType= db.Column('roomType', db.String(80), nullable= False)
  roomRate= db.Column('roomRate', db.Float, nullable=False)
  roomNumber= db.Column('roomNumber', db.Integer, nullable=False, unique=True, primary_key=True)
  bookings= db.relationship("Booking", backref="room", lazy= True)
  available = db.Column('available', db.Boolean, nullable=False, default= True)

  def book(self):
    self.available= False

  def unbook(self):
    self.available= True

  def toDict(self):
    return{
      'roomType' : self.roomType,
      'roomRate' : self.roomRate,
      'roomNumber' : self.roomNumber,
      'bookings' : [booking.toDict() for booking in self.bookings],
     ' available': self.available
    }
  


class Booking(db.Model):
  roomNumber= db.Column('roomNumber', db.Integer, db.ForeignKey('room.roomNumber'), primary_key= True)
  roomType= db.Column('roomType', db.String(80), nullable= False)
  check_in_Date= db.Column(db.DateTime, default=datetime.datetime.utcnow)
  check_out_Date= db.Column(db.DateTime)
  userEmail= db.Column('email', db.String(120), db.ForeignKey("user.email")) 

  def toDict(self):
      return{
        'roomNumber' : self.roomNumber,
        'roomType' : self.roomType,
        'check_in_Date' : self.check_in_Date.strftime("%Y-%m-%d"),
        'check_out_Date' : self.check_out_Date.strftime("%Y-%m-%d")
      }


class Bill(db.Model):
  roomType= db.Column(db.String(120), nullable=False)
  roomNumber= db.Column(db.Integer, db.ForeignKey('room.roomNumber'), primary_key= True) 
  roomRate= db.Column( db.Float, nullable= False)
  check_in_Date= db.Column(db.DateTime, default=datetime.datetime.utcnow)
  check_out_Date= db.Column(db.DateTime)
  paid= db.Column('paid', db.Boolean, nullable=False, default= False)
  #Added a Number of days field
  numberDays = db.Column (db.Integer , nullable=False)
  price= db.Column( db.Float, nullable= False)
  userEmail= db.Column('email', db.String(120), db.ForeignKey("user.email"))  

  def calculateBill(self):
    self.numberDays= (self.check_out_Date - self.check_in_Date).days
    if self.numberDays== 0:
      self.numberDays= 1

    self.price = self.numberDays * self.roomRate
    
  def pay(self):
    self.paid= True

  #added the toDict
  def toDict(self):
    return{
      'roomType' : self.roomType,
      'roomNumber' : self.roomNumber,
      'roomRate' : self.roomRate,
      'check_in_Date' : self.check_in_Date.strftime("%Y-%m-%d"),
      'check_out_Date' : self.check_out_Date.strftime("%Y-%m-%d"),
      'price' : self.price,
      'userEmail' : self.userEmail,
      'paid': self.paid

    }


#For Billing i assume it would be per Days? ( Need uniformed decision )




