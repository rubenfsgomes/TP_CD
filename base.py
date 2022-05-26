from platform import machine
from pydoc import classname
from flask import Flask, abort, jsonify, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate
import numpy as np


from sqlalchemy import false, null, ForeignKey

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' % self.id

class Simulation(db.Model):
    __tablename__ = "simulation"
    id = db.Column(db.Integer, primary_key=True)
    numMaquinas =  db.Column(db.Integer, nullable=False)
    numOperacoes =  db.Column(db.Integer, nullable=False)
    numTrabalhos =  db.Column(db.Integer, nullable=False)
    completed = db.Column(db.Integer, default=0)
    maquinas = db.relationship('Machine', backref='simulation', lazy=True)
    operacoes = db.relationship('Operation', backref='simulation', lazy=True)
    trabalhos = db.relationship('Job', backref='simulation', lazy=True)
    table = db.relationship("Table", uselist=False, backref="simulation")

    def __repr__(self):
        return '<simulation %r>' % self.id

class Machine(db.Model):
    __tablename__ = "machine"
    id = db.Column(db.Integer, primary_key=True)
    simul_id = db.Column(db.Integer, db.ForeignKey('simulation.id'), nullable=False)
    operacoes = db.relationship('Operation', backref='machine', lazy=True)

    def __repr__(self):
        return '<machine %r>' % self.id

class Operation(db.Model):
    __tablename__ = "operation"
    id = db.Column(db.Integer, primary_key=True)
    simul_id = db.Column(db.Integer, db.ForeignKey('simulation.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    maq_id = db.Column(db.Integer,db.ForeignKey('machine.id'),nullable=False)
    duration = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<operation %r>' % self.id

class Job(db.Model):
    __tablename__ = "job"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    simul_id = db.Column(db.Integer, db.ForeignKey('simulation.id'), nullable=False)
    operacoes = db.relationship('Operation', backref='job', lazy=True)

    def __repr__(self):
        return '<job %r>' % self.id

class Operacao:
    def __init__(self, idMachine, duration):
        self.idMachine = idMachine
        self.duration = duration

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

        for i in range(int(numTrab)):
            for j in range(int(numTrab)):
                obj = Operacao(-1, -1)
                operations.append(obj)
            jobs.append(operations) 
        simulations.append(jobs)
        return redirect("/createSimul")
    else:
        return render_template('simul.html', simulations=simulations)

@app.route('/simulations', methods=['GET'])
def get_simulations():
    return jsonify({'simulations': simulations})

class Table(db.Model):
    __tablename__="table"
    id = db.Column(db.Integer, primary_key=True)
    simulation_id= db.Column(db.Integer, ForeignKey('simulation.id'))

if __name__ == "__main__":
    app.run(debug=True)
'''
@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        simul_maq = request.form['numMaq']
        simul_op = request.form['numOp']
        simul_trab = request.form['numTrab']
        new_simul = Simulation(numMaquinas=simul_maq, numOperacoes=simul_op, numTrabalhos=simul_trab)

        try:
            db.session.add(new_simul)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding that simulation'
    else:
        simuls = Simulation.query.all()
        return render_template('index.html', simuls=simuls)

@app.route('/create_machine/<int:id>', methods=['POST', 'GET'])
def create_machine(id):
    simul = Simulation.query.get_or_404(id)
    for i in range(int(simul.numMaquinas)):
        new_maq=Machine(simul_id=id)
        try:
            db.session.add(new_maq)
            db.session.commit()
            return redirect('table/<id>')
        except:
            return 'There was an issue adding that machine'

    if request.method == 'POST':
        new_maq = Machine(simul_id=id)
        try:
            db.session.add(new_maq)
            db.session.commit()
            return 'done'
        except:
            return 'There was an issue adding that machine'
    else:
        maqs = Machine.query.all()
        return render_template('index.html', maqs=maqs)



@app.route('/delete/<int:id>')
def delete(id):
    simul_to_delete = Simulation.query.get_or_404(id)

    try:
        db.session.delete(simul_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that task'

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    simul = Simulation.query.get_or_404(id)
    if request.method == 'POST':
        simul.numMaquinas = request.form['numMaq']
        simul.numOperacoes = request.form['numOp']
        simul.numTrabalhos = request.form['numTrab']
        try:
            db.session.commit()
            return redirect("/")
        except:
            return 'There was a problem updating that task'
    else:
        return render_template('update.html', simul=simul)

@app.route('/create_job/<int:id>', methods=['GET', 'POST'])
def create_job(id):
    simul = Simulation.query.get_or_404(id)
    if request.method == 'POST':
        nome = request.form['jobnome']
        new_job = Job(simul_id=id, nome=nome)
        try:
            db.session.add(new_job)
            db.session.commit()
            return redirect("/")
        except:
            return 'There was an issue adding that simulation'
    else:
        jobs = Job.query.filter_by(simul_id=id)
        return render_template('job.html', jobs=jobs, simul=simul)

@app.route('/create_operation/<int:id>', methods=['GET', 'POST'])
def create_operation(id, id2):
    simul = Simulation.query.get_or_404(id)
    if request.method == 'POST':
        nome = request.form['jobnome']
        maq = request.form['idmaq']
        new_op = Operation(simul_id=id, nome=nome, maq_id=id2)
        try:
            db.session.add(new_op)
            db.session.commit()
            return redirect("/")
        except:
            return 'There was an issue adding that simulation'
    else:
        jobs = Job.query.filter_by(simul_id=id)
        return render_template('job.html', jobs=jobs, simul=simul)
        
@app.route('/table/<int:id>', methods=['GET','POST']) 
def table(id):
    simul = Simulation.query.get_or_404(id)

    return  render_template('table.html', simul=simul)
'''