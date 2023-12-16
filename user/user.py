import requests
import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
from cryptography.fernet import Fernet

app = Flask(__name__)
port = int(os.environ.get('PORT', 5000))
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:abc123@localhost/uts'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = Fernet.generate_key()

db = SQLAlchemy(app)
cipher_suite = Fernet(app.config['SECRET_KEY'].decode())

# ENKRIPSI DATA
def encrypt_data(data):
    return cipher_suite.encrypt(data.encode()).decode()

# DEKRIPSI DATA
def decrypt_data(data):
    return cipher_suite.decrypt(data.encode()).decode()

class User(db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    nama     = db.Column(db.String(50), nullable=False)
    role     = db.Column(db.String(10), nullable=False)

@app.route("/")
def home():
    return "UTS PEMROGRAMAN PL/SQL UNSIA - MICROSERVICE CRUD API"
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=port)

# CRUD USER
# CREATE
@app.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    nama     = data.get('nama')
    role     = data.get('role')

    encrypted_password = encrypt_data(password)

    new_user = User(username=username, password=encrypted_password, nama=nama, role=role)

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User created successfully'}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Username already exists'}), 400

# READ
@app.route('/user/<username>', methods=['GET'])
def get_user(username):
    try:
        user = User.query.filter_by(username=username).one()
        return jsonify({'role':user.role,'nama':user.nama,'username': user.username})
    except NoResultFound:
        return jsonify({'error': 'User not found'}), 404
    
# UPDATE
@app.route('/user/<username>', methods=['PUT'])
def update_user(username):
    try:
        user = User.query.filter_by(username=username).one()
        data = request.get_json()
        new_password = data.get('new_password')
        new_name     = data.get('new_name')
        new_role     = data.get('new_role')

        encrypted_new_password = encrypt_data(new_password)

        user.password = encrypted_new_password
        user.nama     = new_name
        user.role     = new_role
        
        db.session.commit()
        return jsonify({'message': 'User updated successfully'})
    except NoResultFound:
        return jsonify({'error': 'User not found'}), 404
    
# DELETE
@app.route('/user/<username>', methods=['DELETE'])
def delete_user(username):
    try:
        user = User.query.filter_by(username=username).one()
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted successfully'})
    except NoResultFound:
        return jsonify({'error': 'User not found'}), 404