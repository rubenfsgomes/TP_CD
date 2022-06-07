from lib2to3.pgen2.token import OP
from flask import Flask, abort, jsonify,render_template,request,url_for,redirect,flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate
from wtforms import (IntegerField)
from forms import *
from JobShopGoogle import JobShopGoogle
import json
import os
from flask_login import login_user, LoginManager, login_required, logout_user, UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from  flask_login import LoginManager, login_user


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
            return redirect('/createSimul')
        flash('Invalid email address or Password.')    
    return render_template('login.html', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/delete/user/<int:id>", methods=['GET', 'POST'])
def deleteUser(id):
    User.query.filter(User.id == id).delete()

def generate_field_for_question(question):
    return IntegerField(question.text)

operations = []
jobs = [{'id': 1}]

simulations = [{'id': 1,
                'numMac': 2,
                'numOp': 2,
                'numJob': 2,
                'jobs': [operations]}]

@app.route('/createSimul', methods=['POST', 'GET'])
@login_required
def create_simulation():
    if request.method == 'POST':
        numMac = request.form['numMaq']
        numOp = request.form['numOp']
        numJob = request.form['numTrab']
        simulation = {
            'id': simulations[-1]['id'] + 1,
            'numMac': [numMac],
            'numOp': [numOp],
            'numJob': [numJob]
        }
        simulations.append(simulation)
        return redirect("/createSimul")
    else:
        return render_template('simul.html', simulations=simulations)

@app.route("/simulations", methods=['GET'])
@login_required
def get_sims():
    return jsonify({'simulations': simulations})

@app.route("/simulation/delete/<int:id>", methods=['DELETE', 'POST', 'GET'])
@login_required
def delete_sim(id):
    for sim in simulations:
        if sim['id'] == id:
            simulation = sim
    simulations.remove(simulation)
    return redirect("/createSimul")

@app.route("/addoperation/<int:idSim>/<int:idJob>", methods=['GET','POST'])
@login_required
def addOperation(idSim, idJob):
    if request.method == 'POST':
        for sim in simulations:
            if sim['id'] == idSim:
                simulation = sim

        idOp = request.form['idOp']
        idMaq = request.form['idMaq']
        duration = request.form['duration']

        operation = {
            'id': idOp,
            'maq': idMaq,
            'duration': duration
        }

        for job in jobs:
            if job['id'] == idJob:
                jobToAdd = job

        if len(jobToAdd)==0:
            jobToAdd = {
                'id': idJob,
                'operation':[operation]
            }
        else:
            for op in job['operation']:
                if op['id'] == operation['id']:
                    return 'Operation exists in simulation'
            job['operation'].append(operation)
        jobs.append(job)
        simulation['jobs'] = jobs
        return redirect("/createSimul")
    else:
        return render_template("operation.html")

@app.route("/simul", methods=["GET","POST"])
@login_required
def simulFill():
    if request.method=="GET":
        return render_template("index.html")
    else:
        data=request.get_json()["data"]
        data=data[1:]
        forTable=[]
        for objs in data:
            j=0
            dataToAdd=[]            
            for obj in objs:
                toAdd=(j,int(obj))
                dataToAdd.append(toAdd)
                j+=1
            forTable.append(dataToAdd)
        listOfData,tps=JobShopGoogle().JobShopData(forTable)
        return  json.dumps({"time":tps,"data":listOfData})
        
if __name__ == "__main__":
    app.run(debug=True)
