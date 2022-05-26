from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate

from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

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
    numMaquinas = completed = db.Column(db.Integer, nullable=False)
    numOperacoes = completed = db.Column(db.Integer, nullable=False)
    numTrabalhos = completed = db.Column(db.Integer, nullable=False)
    completed = db.Column(db.Integer, default=0)
    maquinas = db.relationship('Machine', backref='simulation', lazy=True)
    operacoes = db.relationship('Operation', backref='simulation', lazy=True)
    trabalhos = db.relationship('Job', backref='simulation', lazy=True)
    table = relationship("Table", back_populates="simulation", uselist=False)

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
    machine_id = db.Column(db.Integer, db.ForeignKey('machine.id'), nullable=True)

    def __repr__(self):
        return '<operation %r>' % self.id

class Job(db.Model):
    __tablename__ = "job"
    id = db.Column(db.Integer, primary_key=True)
    simul_id = db.Column(db.Integer, db.ForeignKey('simulation.id'), nullable=False)
    operacoes = db.relationship('Operation', backref='job', lazy=True)

    def __repr__(self):
        return '<job %r>' % self.id

class Table(db.Model):
    __tablename__ = "table"
    id = db.Column(db.Integer, primary_key=True)
    simulation = relationship("Simulation", back_populates="table", uselist=False)

@app.route('/create_job/<int:id>')

@app.route('/create_table/<int:id>', methods=['GET', 'POST'])
def createTable(id):
    simul = Simulation.query.get_or_404(id)

    for i in range(simul.numTrabalhos):
        new_job = Job(simul_id=simul.id)

        try:
            db.session.add(new_job)
            simul.trabalhos.append(new_job)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding that simulation'

    return render_template('table.html')
    
    

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



@app.route('/delete/<int:id>')
def delete(id):
    simul_to_delete = Simulation.query.get_or_404(id)

    try:
        db.session.delete(simul_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that simulation'

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
            return 'There was a problem updating that simulation'
    else:
        return render_template('update.html', simul=simul)
    
if __name__ == "__main__":
    app.run(debug=True)
