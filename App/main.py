
import os
import json
from flask_cors import CORS
from flask import Flask, request, jsonify, render_template, redirect, flash, url_for
from flask_login import LoginManager, current_user, login_user, login_required, logout_user
from sqlalchemy.exc import IntegrityError
from models import db, User, Customer #add application models
from models import Room , Booking , Bill
import datetime

''' Begin Flask Login Functions '''
login_manager = LoginManager()
@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()

#N.B. Remember me cookies are for the event a user logs out accidentally

#THE URL TO REDIRECTS USER TO IF THEY ARENT LOGGED IN
login_manager.login_view = "loginForm"
#Store the previous page that required login...and redirects user to it if true
login_manager.use_session_for_next= False

#Duration of the login_manager remember me session cookie
login_manager.REMEMBER_COOKIE_DURATION= datetime.timedelta(minutes= 1)
#Prevents client side scripts from accessing it
login_manager.REMEMBER_COOKIE_HTTPONLY= False
#Refreshes cookie on each request: if true
login_manager.REMEMBER_COOKIE_REFRESH_EACH_REQUEST= True
''' End Flask Login Functions '''


''' Begin boilerplate code '''

def get_db_uri(scheme='sqlite://', user='', password='', host='//demo.db', port='', name=''):
    return scheme+'://'+user+':'+password+'@'+host+':'+port+'/'+name 

def loadConfig(app):
    #try to load config from file, if fails then try to load from environment
    try:
        app.config.from_object('App.config')
        app.config['SQLALCHEMY_DATABASE_URI'] = get_db_uri() if app.config['SQLITEDB'] else app.config['DBURI']
    except:
        print("config file not present using environment variables")
        # DBUSER = os.environ.get("DBUSER")
        # DBPASSWORD = os.environ.get("DBPASSWORD")
        # DBHOST = os.environ.get("DBHOST")
        # DBPORT = os.environ.get("DBPORT")
        # DBNAME = os.environ.get("DBNAME")
        DBURI = os.environ.get("DBURI")
        SQLITEDB = os.environ.get("SQLITEDB", default="true")
        app.config['ENV'] = os.environ.get("ENV")
        app.config['SQLALCHEMY_DATABASE_URI'] = get_db_uri() if SQLITEDB in {'True', 'true', 'TRUE'} else DBURI



def create_app():
  app = Flask(__name__, static_url_path='/static')
  loadConfig(app)
  
  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
  app.config['TEMPLATES_AUTO_RELOAD'] = True
  app.config['PREFERRED_URL_SCHEME'] = 'https'
  CORS(app)
  db.init_app(app)
  login_manager.init_app(app)
  return app

app = create_app()

app.app_context().push()

''' End Boilerplate Code '''


#find user and pass to home.html if logged in


@app.route('/', methods=['GET']) 
def home():
  
  if current_user.is_authenticated:
    user= User.query.filter_by(email= current_user.email).first()
    user= user.toDict()
    return render_template('Home.html', user= user)
  return render_template('Home.html')


@app.route('/signupForm', methods=['GET'])
def display_signup():
  return render_template('Signup.html')

@app.route('/rooms') 
def display_rooms():
  rooms = Room.query.all()
  if current_user.is_authenticated:
    user= User.query.filter_by(email= current_user.email).first()
    user= user.toDict()
    return render_template('Room.html', user= user , rooms=rooms)
  return render_template('Room.html' , rooms=rooms)

@app.route('/about') 
def display_about():
  if current_user.is_authenticated:
    user= User.query.filter_by(email= current_user.email).first()
    user= user.toDict()
    return render_template('About.html', user = user)
  return render_template('About.html')

@app.route('/loginForm', methods=['GET'])
def loginForm():
  return render_template('Login.html')
  

@app.route('/signup', methods=['POST'])
def sign_up():
  data= request.form  # get json data (aka submitted login_id, email & password)
  
  if data == None:
    flash("Invalid request.")
    return redirect("/")

  if data['password'] !=data['confirm_password']:
    flash("Passwords must match!")
    return redirect(url_for('display_signup'))

  elif data['password']=='' or data['email']=='':
    flash("Email and password fields must be filled!")
    return redirect(url_for('display_signup'))

  try:
    
    user = User( email=data['email'])
    user.set_password( data['password'])
    customer= Customer(email= data['email'], firstName= data['firstName'], lastName= data['lastName'], phoneNumber= data['phoneNumber'], country=data['country'], address= data['address'])
    db.session.add(user)
    db.session.add(customer)
    db.session.commit()
  except IntegrityError:
    db.session.rollback()
    flash('Sign up failed: Account could not be created.')
    return redirect(url_for("display_signup") )
    
  flash(" Account created")
  return redirect('/loginForm')
  
    
@app.route('/login', methods=['POST'])
def login():   
  data= request.form
  if data['email']!='' and data['password']!='':
    user= User.query.filter_by(email=data['email']).first()
    if user and user.check_password(data['password']):
      
      login_user( user, remember=True, duration= datetime.timedelta(hours= 1) )
      flash("You have logged in successfully")
 
      return redirect( url_for(".display_rooms") )
    
    flash("Login Failed: Invalid User email or password. ")
    return redirect( url_for('.loginForm') )

  flash("Login Failed: please Enter your credentials before submitting. ")
  return redirect( url_for('.loginForm') )
  
  
@app.route("/logout")
@login_required
def logout():
  logout_user()
  flash('Logged Out!')
  return redirect(url_for('.home'))




@app.route("/book/<roomType>/<roomNumber>", methods=["GET"])
@login_required
def display_booking(roomType , roomNumber):

  if current_user.is_authenticated:
    user= User.query.filter_by(email= current_user.email).first()
    user= user.toDict()
    return render_template('Book.html', user= user, roomNumber= roomNumber, roomType= roomType)

  return render_template( "/loginForm" )


#Adds a booking: includes creating a bill & book room
@app.route("/book/<roomType>/<roomNumber>", methods=["POST"])
@login_required
def addBooking(roomType , roomNumber):  
  data= request.form

  if data and current_user.is_authenticated:
    #Get the current user's info: for tab bar
    user= User.query.filter_by(email= current_user.email).first()
    user= user.toDict()

    #Get dates for calculation
    endDate = data['trip-end']
    startDate = data['trip-start']

    

    #Split Date Strings into [year, month, day]
    endDate = data['trip-end'].split('-')
    startDate = data['trip-start'].split('-')
    #Create Date object using datetime
    d1= datetime.datetime( int(endDate[0]), int(endDate[1]), int(endDate[2]) )
    d2= datetime.datetime( int(startDate[0]), int(startDate[1]), int(startDate[2])  )
    print(endDate)
    print(startDate)
    print("Room \n\n",  type(roomNumber) )

    #Note
    #Initially you had the check out date being store as the check in date and vice versa

    #Make Booking object
    booking = Booking( roomNumber = int(roomNumber) , roomType = roomType , check_in_Date= d2 , check_out_Date=d1 , userEmail= current_user.email)
    #Get room and 
    room = Room.query.filter_by(roomNumber= int(roomNumber) ).first()
    #set room.available=False
    room.book()

    try:
      db.session.add(booking)
      db.session.add(room)
      db.session.commit()

      #Create Bill - Once booking is sucessful
      room= Room.query.filter_by(roomType = roomType).first()
      roomRate = room.roomRate
      print("Room rate: ",roomRate)

      
      bill = Bill(roomNumber = int(roomNumber) , roomType = roomType , check_in_Date= d2 , check_out_Date=d1 , userEmail= current_user.email , roomRate = float(roomRate) )

      bill.calculateBill()
      try:
        db.session.add(bill)
        db.session.commit()
      except IntegrityError:
        db.session.rollback()
      
      flash("Your room has been successfully booked.")
      return redirect("/MyBookings")
      
    except IntegrityError:
      db.session.rollback()
      flash("Your booking already exist.")
    
    return render_template('Book.html', user= user, roomNumber= roomNumber, roomType= roomType)

  flash("Invalid request.")
  return redirect("/loginForm")




#Route for a specific room type
@app.route('/rooms/<roomType>')
@login_required
def display_roomType(roomType):

  rooms = Room.query.filter_by(roomType = roomType , available=True)

  roomCount=0
  for room in rooms:
    roomCount = roomCount + 1


  rooms = Room.query.filter_by(roomType = roomType , available=True).first()

  if current_user.is_authenticated:
    user= User.query.filter_by(email= current_user.email).first()
    user= user.toDict()
    return render_template('Roomtype.html', user= user , roomType = roomType , rooms = rooms , roomCount = roomCount)
  
  return render_template('Roomtype.html' , roomType = roomType , rooms = rooms,roomCount = roomCount)




@app.route('/MyBookings')
@login_required
def display_bookings():

  if current_user.is_authenticated:
    user= User.query.filter_by(email= current_user.email).first()
    user= user.toDict()

    userbooking= user['bookings']
    
    return render_template('Userbookings.html' , user=user , bookingdetails= userbooking)
  
  flash("Only logged in users can access the previous page!")
  return redirect("/loginForm")

  

@app.route('/MyAccount')
@login_required
def display_AcountDetails():

  if current_user.is_authenticated:
    user= User.query.filter_by(email= current_user.email).first()
    user= user.toDict()

    accountdetails = Customer.query.filter_by(email= current_user.email).first()

  return render_template('Userdetails.html' , user=user , accountdetails=accountdetails)


#Deletes booking & unbook Room: including, booking, bill
@app.route("/delete/<roomType>/<roomNumber>", methods=['GET'])
@login_required
def delete_booking(roomType, roomNumber):
  if current_user.is_authenticated:
    booking = Booking.query.filter_by(userEmail= current_user.email, roomType= roomType, roomNumber= int(roomNumber) ).first()
    if booking!=None:
      

      room = Room.query.filter_by(roomNumber= int(roomNumber) ).first()
      #set room.available=False
      room.unbook()

      bill= Bill.query.filter_by(userEmail= current_user.email, roomType= roomType, roomNumber= int(roomNumber) ).first()

    try:
      db.session.delete(booking)
      db.session.delete(bill)
      #room is not deleted but updated, so we just add the update
      db.session.add(room)
      db.session.commit()
      flash("Your booking has been successfully deleted.")
      
    except:
      db.session.rollback()
      flash("Booking failed to delete.")
    user= User.query.filter_by(email= current_user.email).first()
    user= user.toDict()

    userbooking= user['bookings']
    
    return render_template('Userbookings.html' , user=user , bookingdetails= userbooking)

  flash("Only logged in users can access the previous page!")
  return redirect("/loginForm")

#Edit user account details
@app.route("/MyProfile/edit", methods=['POST'])
@login_required
def edit_account():
  data= request.form  # get json data (aka submitted login_id, email & password)
  
  if data != None:
    if data['password'] !=data['confirm_password']:
      flash("Passwords must match!")
      return redirect("/MyProfile")

    

    user= User.query.filter_by(email= current_user.email).first()
    
    if data['firstName'] !='':
      user.customer.firstName= data['firstName']

    if data['lastName'] !='':
      user.customer.lastName= data['lastName']

    if data['password'] !='':
      user.set_password(data['password'])

    if data['country'] !='':
      user.customer.country= data['country']
    
    if data['phoneNumber'] !='':
      user.customer.phoneNumber= data['phoneNumber']

    if data['address'] !='':
      user.customer.address= data['address']

    try:
      
      db.session.add(user)
      db.session.commit()
      
    except IntegrityError:
      db.session.rollback()
      flash('Update failed: Account could not be updated.')
      return redirect("/MyProfile" )
    
    flash("Your account has been successfully updated.")
    #return redirect('/MyProfile')
    return redirect('/MyAccount')
  
  flash("No Data has been captured.")
  return redirect('/MyProfile')


@app.route('/MyBookings/updateForm/<roomType>/<roomNumber>', methods=['GET']) 
@login_required
def display_booking_updateForm(roomType, roomNumber):
  user= User.query.filter_by(email= current_user.email).first()
  user= user.toDict()
  booking = Booking.query.filter_by(userEmail= current_user.email, roomType= roomType, roomNumber= int(roomNumber) ).first()
  booking= booking.toDict()
  return render_template('Updateuserbookings.html', user= user, booking= booking)


#Updates a user booking and bill
#Updates a user booking and bill
@app.route('/MyBookings/updateForm/<roomType>/<roomNumber>', methods=['POST']) 
@login_required
def update_booking(roomType, roomNumber):
  data= request.form
  if roomType==None or roomNumber==None or data==None:
    flash("An invalid request was attempted.")
    return redirect("/")
  
  endDate = data['trip-end']
  startDate = data['trip-start']

  booking = Booking.query.filter_by(userEmail= current_user.email, roomType= roomType, roomNumber= int(roomNumber) ).first()



  booking.check_in_Date = datetime.datetime.strptime(startDate, "%Y-%m-%d").date()
  booking.check_out_Date = datetime.datetime.strptime(endDate, "%Y-%m-%d").date()
   
  bill= Bill.query.filter_by(userEmail= current_user.email, roomType= roomType, roomNumber= int(roomNumber) ).first()

  #Create a date objects to add to bill
  bill.check_in_Date = datetime.datetime.strptime(startDate, "%Y-%m-%d").date()
  bill.check_out_Date = datetime.datetime.strptime(endDate, "%Y-%m-%d").date()

  bill.calculateBill()

  try: 
    db.session.add(booking)
    db.session.add(bill)
    db.session.commit()

    flash("Update was successful.")
    
  except: 
    db.session.rollback()
    flash("Update failed.")

  return redirect("/MyBookings")


@app.route('/deleteUser', methods=['POST'])
@login_required
def delete_user():
  user= User.query.filter_by(email= current_user.email).first()
  customer= Customer.query.filter_by(email= current_user.email).first()

  bookings= Booking.query.all()

  

  try:
    if bookings != None:
      for booking in bookings:
        if booking.userEmail == current_user.email:
        
          room= Room.query.filter_by(roomNumber= booking.roomNumber).first()
          room.unbook()
          
          bill= Bill.query.filter_by(roomNumber=booking.roomNumber, userEmail= current_user.email, check_in_Date= booking.check_in_Date).first()

          
          db.session.add(room)
          db.session.delete(booking)
          db.session.delete(bill)

    db.session.delete(customer)
    db.session.delete(user)
    db.session.commit()
    flash("Your account has been successfully deleted.")
  except:
    db.session.rollback()
    flash("You failed to delete your account")
    return redirect (request.referrer)
  
  return redirect("/")




@app.route('/MyBill/<roomNumber>', methods=['GET'])
@login_required
def display_bill(roomNumber):
  
  if current_user.is_authenticated:
    user= User.query.filter_by(email= current_user.email).first()
    user= user.toDict()

    bill = Bill.query.filter_by(roomNumber= int(roomNumber)).first() 

    return render_template('Userbill.html' , user = user , bill = bill)

  return redirect("/MyBookings")

@app.route('/MyBill/<roomNumber>/pay', methods=['POST'])
@login_required
def pay_bill(roomNumber):
  bill = Bill.query.filter_by(roomNumber= int(roomNumber)).first() 

  if bill== None:
    flash("An Invalid request was made.")
    return redirect('/MyBookings')

  if bill.paid is True:
    flash("Your bill has already been paid.")
    return redirect(request.referrer)

  bill.pay()
  try:
    db.session.add(bill)
    db.session.commit()
    flash("You have successful paid your bill.")

  except: 
    db.session.rollback()
    flash("Attempt to pay bill failed.")

  return redirect(request.referrer)


 #TEST 
@app.route('/users', methods=['GET'])
def all_users():
  users= User.query.all();
  users= [user.toDict() for user in users]
  return jsonify(users)


@app.route("/bills", methods=["GET"])
def display_bills():
  bills= Bill.query.all()
  bills= [bill.toDict() for bill in bills]
  return jsonify(bills)

@app.route('/r') 
def all_rooms():
  rooms= Room.query.all();
  rooms = [room.toDict() for room in rooms];
  return jsonify(rooms)

@app.route('/b')
def display_book():
  return render_template('Book.html')

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080, debug=True)


