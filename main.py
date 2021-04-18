import json
from flask_cors import CORS
from flask import Flask, request, jsonify, render_template, redirect, flash, url_for
from flask_login import LoginManager, current_user, login_user, login_required, logout_user
from sqlalchemy.exc import IntegrityError
from models import db, User, Customer #add application models
from models import Room
import datetime

''' Begin Flask Login Functions '''
login_manager = LoginManager()
@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()

#N.B. Remember me cookies are for the event a user logs out accidentally

#THE URL TO REDIRECTS USER TO IF THEY ARENT LOGGED IN
login_manager.login_view = "loginForm"
#Duration of the login_manager remember me session cookie
login_manager.REMEMBER_COOKIE_DURATION= datetime.timedelta(minutes= 1)
#Prevents client side scripts from accessing it
login_manager.REMEMBER_COOKIE_HTTPONLY= False
#Refreshes cookie on each request: if true
login_manager.REMEMBER_COOKIE_REFRESH_EACH_REQUEST= True
''' End Flask Login Functions '''


''' Begin boilerplate code '''


def create_app():
  app = Flask(__name__, static_url_path='')
  app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
  app.config['SECRET_KEY'] = "MYSECRET"
  CORS(app)
  db.init_app(app)
  login_manager.init_app(app)
  return app

app = create_app()

app.app_context().push()

''' End Boilerplate Code '''


#find user and pass to home.html if logged in


@app.route('/', methods=['GET']) 
@login_required
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
def display_Rooms():
  rooms = Room.query.all()
  return render_template('Room.html' , rooms=rooms)

@app.route('/about') 
def display_about():
	return render_template('About.html')

@app.route('/loginForm', methods=['GET'])
def loginForm():
  return render_template('Login.html')

@app.route('/signup', methods=['POST'])
def sign_up():
  data= request.form  # get json data (aka submitted login_id, email & password)
  
  if data['password'] !=data['confirm_password']:
    flash("Passwords must match!")
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
  if data:
    user= User.query.filter_by(email=data['email']).first()
    if user and user.check_password(data['password']):
      
      login_user( user, remember=True, duration= datetime.timedelta(hours= 1) )
      flash("You have logged in successfully")
      return redirect( url_for('home') )
    
  flash("Login Failed; Invalid User email or password. ")
  return redirect( url_for('.loginForm') )
  
@app.route("/logout")
@login_required
def logout():
  logout_user()
  flash('Logged Out!')
  return redirect(url_for('.home'))


  
@app.route('/users', methods=['GET'])
def all_users():
  users= User.query.all();
  users= [user.toDict() for user in users]
  return jsonify(users)

#Just trying something
@app.route('/rooms/<roomType>')
def display_rooms(roomType):
  rooms = Room.query.filter_by(roomType = roomType , available=True)
  rooms= [room.toDict() for room in rooms];
  return jsonify( rooms)
  return render_template('Roomtype.html' , roomType = roomType , rooms = rooms)

#this page is gonna be for when the user clicks view..the booking page? what sahrah sent in the chat where the user clicks view
#and the page for that type of room compile#im going to attempt it atleast
#cool , no prob
#Btw i edited the sign up form...i realize login_id isnt needed so i left it out
#Cool , i dont remmebr having a login id XD , but makes sense




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
