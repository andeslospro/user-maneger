from flask import Flask, request, jsonify
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
import datetime
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from flask_jwt_extended import JWTManager

import hashlib
app = Flask(__name__)
api = Api(app)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///database2.db'
app.config["JWT_SECRET_KEY"] = 'b74304655f486e70d866914e0dca1cfc'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(minutes=5)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = datetime.timedelta(minutes=5)
jwt = JWTManager(app)
db = SQLAlchemy(app)
app.app_context().push()

class UserData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    def __repr__(self):
       return f"Parameters post(name = {self.name}, email = {self.email})"
    
class UsersAPI(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    def __repr__(self):
        return f"User(Username post = {self.username}, password =  {self.password})"

def get_all_users():
    users = UserData.query.all()
    user_list = [{'name': user.name, 'email': user.email} for user in users]
    return user_list



@app.route('/register_ussers', methods=['POST'])
def regiser_user():
    data = request.json
    username = data.get('username')
    password = hashlib.sha256(data['password'].encode()).hexdigest()

    if not username or not password:
        return jsonify({'message': 'Username and Password required'}),400
    
    if UsersAPI.query.filter_by(username=username).first():
         return jsonify({'message':'Username already exist'}), 400
    
    new_user = UsersAPI(username = username, password = password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message':'User registered successfully'}), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username', '')
    password = hashlib.sha256(data['password'].encode()).hexdigest()

    user = UsersAPI.query.filter_by(username = username).first()
    if not user or not user.password == password:
        return jsonify({'message': 'Invalid username or password',
                        "user": username,
                        "pass":password}), 401
   

    access_token = create_access_token(identity=user.id)
    return jsonify({"access_token":access_token,
                   "user": username,
                   "pass": password
                   }), 200
     

@app.route('/add_us_db', methods=['POST'])
@jwt_required()
def add_user():
    current_user = get_jwt_identity()
    data = request.json
    name = data.get('name')
    email = data.get('email')
    if name and email:
        new_user = UserData(name = name, email = email)
        db.session.add(new_user)
        db.session.commit()
        print (new_user)
        return jsonify({'message': 'User added successfully'}, ), 201
        
    else:
        return jsonify({'error': 'Name and email required'}), 400   


@app.route('/get_all_us', methods=['GET'])
@jwt_required()
def get_user():
    users = get_all_users()
    return jsonify({"usr":users})    

if __name__ == '__main__':
     with app.app_context():
         db.create_all()
     app.run(debug=True)

     