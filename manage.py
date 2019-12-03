import os
from flask import Flask, jsonify, request
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from models import db, User
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)



BASEDIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret-key"
app.config['JWT_SECRET_KEY'] = 'encrypt'
app.config["DEBUG"] = True
app.config["ENV"] = "development"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASEDIR, "test.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
jwt = JWTManager(app)
bcrypt = Bcrypt(app)
Migrate = Migrate(app,db)
CORS(app) 


Manager = Manager(app)
Manager.add_command("db" , MigrateCommand)

@app.route("/login",methods=["POST"])
def login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if not username:
        return jsonify({"msg": "Missing username parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400
    
    user = User.query.filter_by(username=username).first()
    #return jsonify(user.serialize()), 200
    if user is None:
        return jsonify({"msg": "Username not found"}), 404
    
    if bcrypt.check_password_hash(user.password, password):
        access_token = create_access_token(identity=username)
        data = {
            "access_token": access_token,
            "user" : user.serialize(),
            "msg": "success"
        }
        return jsonify(data), 200


    
@app.route("/users", methods=["GET","POST"])
@app.route("/users/<int:id>", methods=["GET","PUT","DELETE"])
def user(id=None):
    if request.method == "GET":
        if id is not None:
            user = User.query.filter_by(id)

            return jsonify(user.serialize()), 200
        else:
            users = User.query.all()

            json_lists = [user.serialize() for user in users]

            return jsonify(json_lists), 200

    if request.method == "POST":
        user = User()
        user.username = request.json.get("username")
        pw_hash = bcrypt.generate_password_hash(request.json.get("password"))
        user.password = pw_hash
        user.email = request.json.get("email")
        user.firstname = request.json.get("firstname")
        user.lastname = request.json.get("lastname")
        user.gender = request.json.get("gender")
        
        db.session.add(user)

        db.session.commit()

        return jsonify({"success": True}), 201 

    if request.method == "PUT":
        if id is not None: 
            user = User.query.get(id)
            user.email = request.json.get("email")
            db.session.commit()
            return jsonify(user.serialize()), 201

    if request.method == "DELETE":
        if id is not None:
            user = User.query.get(id)
            db.session.delete(user)
            db.session.commit()
            return jsonify({"msg":"User has been deleted"}), 201



if __name__ == "__main__":
    Manager.run()
