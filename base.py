from lib2to3.pgen2.token import OP
from platform import machine
from pydoc import classname
from tkinter import E
from tkinter.tix import Form
from turtle import clear
from flask import Flask,render_template,request,url_for,redirect,flash,jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate
import numpy as np
from flask_wtf import FlaskForm
from wtforms import (StringField, TextAreaField, IntegerField, BooleanField, DateField,
                     RadioField)
from forms import *
from wtforms.validators import InputRequired, Length
from werkzeug.utils import secure_filename
from JobShopGoogle import JobShopGoogle
import json
import os
from flask_login import login_user, LoginManager, login_required, logout_user, UserMixin
from datetime import datetime
from sqlalchemy import false, null, ForeignKey
from werkzeug.security import generate_password_hash, check_password_hash
from  flask_login import LoginManager, login_user, current_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydb.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
login_manager = LoginManager()
login_manager.init_app(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(UserMixin, db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(50), index=True, unique=True)
  email = db.Column(db.String(150), unique = True, index = True)
  password_hash = db.Column(db.String(150))
  joined_at = db.Column(db.DateTime(), default = datetime.utcnow, index = True)

  def set_password(self, password):
        self.password_hash = generate_password_hash(password)

  def check_password(self,password):
      return check_password_hash(self.password_hash,password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route('/register', methods = ['POST','GET'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username =form.username.data, email = form.email.data)
        user.set_password(form.password1.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user is not None and user.check_password(form.password.data):
            login_user(user)
            next = request.args.get("next")
            return redirect('/jobs/add')
        flash('Invalid email address or Password.')    
    return render_template('login.html', form=form)

@app.route("/logout")
# @login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

simulations = [
]

@app.route('/createSimul', methods=['POST', 'GET'])
def create_simulation():
    if request.method == 'POST':
        jobs = []
        operations = []
        numMaq = request.form['numMaq']
        numOp = request.form['numOp']
        numTrab = request.form['numTrab']
        duration = request.form['duration']
        idMachine = request.form['idMachine']

        for i in range(int(numTrab)):
            for j in range(int(numTrab)):
                obj = Operacao(-1, -1)
                operations.append(obj)
            jobs.append(list(operations))
            operations.clear()
        simulations.append(jobs)
        return redirect("/createSimul")
    else:
        return render_template('simul.html', simulations=simulations)

def generate_field_for_question(question):
    return IntegerField(question.text)

@app.route('/table', methods=['POST', 'GET'])
def create_table():
    if request.method == 'POST':
        duration = request.form['duration']
        idMachine = request.form['idMachine']
        for jobs in simulations:
            for ops in jobs:
                for op in ops:
                    op.duration = duration
                   
        return redirect("/createSimul")
    else:
        return render_template("table.html", simulations=simulations)

@app.route('/operation', methods=['POST', 'GET'])
def create_operation():
    pass

lst = []

@app.route("/jobs/add", methods=["GET","POST"])
@login_required
def manual():
    if request.method=="GET":
        return render_template("index.html")
    else:
        data=request.get_json()["data"]
        data=data[1:]
        data1=[]
        for d1 in data:
            j=0
            data11=[]            
            for d2 in d1:
                t=(j,int(d2))
                data11.append(t)
                j+=1
            data1.append(data11)
        lst,tps=JobShopGoogle().MinimalJobshopSat(data1)      
        return  json.dumps({"time":tps,"data":lst})
        
if __name__ == "__main__":
    app.run(debug=True)
