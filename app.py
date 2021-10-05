from flask import Flask, jsonify, make_response, request
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemySchema
from sqlalchemy.orm.exc import UnmappedInstanceError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/msql.db'
db = SQLAlchemy(app)

class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    spec = db.Column(db.String(50))

    def __init__(self, name, spec):
        self.name = name
        self.spec = spec

    def __repr__(self):
        return self.name

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

db.create_all() 


class AuthorSchema(SQLAlchemySchema):

    class Meta:
        model = Author
        sqla_session = db.session

    id = fields.Integer(dump_only=True)
    name = fields.String(redirected=True)
    spec = fields.String(required=True)


@app.route('/authors', methods=['GET'])
def index():
    get_authors = Author.query.all()
    author_schema = AuthorSchema(many=True)
    authors = author_schema.dump(get_authors)
    return make_response(jsonify({'authors': authors}))


@app.route('/authors', methods=['POST'])
def create_author():
    data = request.get_json()
    author_schema = AuthorSchema()
    data = author_schema.load(data)
    name, spec = data['name'], data['spec']
    author = Author(name=name, spec=spec)
    db.session.add(author)
    db.session.commit()
    return make_response(jsonify({'author': data}), 201)


@app.route('/authors/<id>', methods=['GET'])
def get_author_by_id(id):
    get_author = Author.query.get(id)
    schema = AuthorSchema()
    author = schema.dump(get_author)
    return make_response(jsonify({'author': author}))


@app.route('/authors/<id>', methods=['PUT'])
def update_author_by_id(id):
    data = request.get_json()
    get_author = Author.query.get(id)
    if data.get('name'):
        get_author.name = data['name']
    if data.get('spec'):
        get_author.spec = data['spec']
    db.session.add(get_author)
    db.session.commit()
    schema = AuthorSchema(only=['id', 'name', 'spec'])
    author = schema.dump(get_author)
    return make_response(jsonify({'author': author}))


@app.route('/authors/<id>', methods=['DELETE'])
def delete_author_by_id(id):
    try:
        get_author = Author.query.get(id)
        db.session.delete(get_author)
        db.session.commit()
    except UnmappedInstanceError:
        return make_response('No author with such id')
    return make_response('', 204)


if __name__ == '__main__':
    app.run(debug=True)