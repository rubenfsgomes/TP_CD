#!flask/bin/python
from flask import Flask, jsonify
from flask import abort, make_response, request

app = Flask(__name__)

simulations = [
    {
        'Numero de Maquinas': 2,
        'Numero de Trabalhos': 1,
        'Numero de Operacoes': 2
    }
]

@app.route('/todo/api/v1.0/simulations', methods=['GET'])
def get_tasks():
    return jsonify({'simulations': simulations})

@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    simulation = [simulation for simulation in simulations if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    return jsonify({'task': simulation[0]})

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.route('/todo/api/v1.0/tasks', methods=['POST'])
def create_task():
    if not request.json or not 'title' in request.json:
        abort(400)
    simulation = {
        'id': simulations[-1]['id'] + 1,
        'title': request.json['title'],
        'description': request.json.get('description', ""),
        'done': False
    }
    simulations.append(simulation)
    return jsonify({'task': simulation}), 201

if __name__ == '__main__':
    app.run(debug=True)