from dataclasses import dataclass
from datetime import datetime, tzinfo
from flask import Flask, jsonify, request, Response
from flask_sqlalchemy import SQLAlchemy
from http import HTTPStatus

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

@dataclass
class Todo(db.Model):
    content: str
    id: int
    pub_date: int

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String, nullable=False)
    pub_date = db.Column(db.DateTime(timezone=True), default=datetime.now())

    def __rep__(self):
        return '<Task %r>' % self.id

@app.route('/tasks', methods=['GET'])
def get_tasks():
    try:
        all_tasks = Todo.query.all()
    except:
        return jsonify(HTTPStatus.INTERNAL_SERVER_ERROR)
    return jsonify(all_tasks), HTTPStatus.OK

@app.route('/tasks', methods=['POST'])
def add():
    task_content = request.form['content']
    if len(task_content) != 0:
        new_task = Todo(content=task_content)
        try:
            db.session.add(new_task)
            db.session.commit()
        except:
            return jsonify(HTTPStatus.INTERNAL_SERVER_ERROR)
    else:
        return jsonify(HTTPStatus.BAD_REQUEST)

    return jsonify(new_task), HTTPStatus.CREATED


@app.route('/tasks/<id>', methods=['DELETE'])
def task_delete(id):  
    task_delete = Todo.query.filter_by(id=id).first_or_404()
    try:
        db.session.delete(task_delete)
        db.session.commit()
    except:
        return jsonify(HTTPStatus.INTERNAL_SERVER_ERROR)

    return jsonify(task_delete), HTTPStatus.FOUND


@app.route('/tasks/<id>', methods=['PATCH'])
def update(id):
    task_update = Todo.query.filter_by(id=id).first_or_404()
    try:
        new_content = request.form['new_content']  
        task_update.content = new_content
        db.session.commit()
    except:
        return jsonify(HTTPStatus.INTERNAL_SERVER_ERROR)

    return jsonify(task_update), HTTPStatus.OK

if __name__ == "__main__":
    app.run(debug=True)