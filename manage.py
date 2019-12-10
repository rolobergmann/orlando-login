import os
import re
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
    email = request.json.get('email', None)
    password = request.json.get('password', None)
    if not email:
        return jsonify({"msg": "Missing email parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400
    
    user = User.query.filter_by(email=email).first()

    if user is None:
        return jsonify({"msg": "Email not found"}), 404
    
    if bcrypt.check_password_hash(user.password, password):
        access_token = create_access_token(identity=email)
        data = {
            "access_token": access_token,
            "user" : user.serialize(),
            "msg": "success"
        }
        return jsonify(data), 200


    
@app.route("/signup", methods=["POST"])
def user():
        #Regular expression that checks a valid email
        ereg = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
        #Regular expression that checks a valid password
        preg = '^.*(?=.{8,})(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).*$'
        # Instancing the a new user
        user = User()
        #Checking email 
        if (re.search(ereg,request.json.get("email"))):
            user.email = request.json.get("email")
        else:
            return "Invalid email format", 400
        #Checking password
        if (re.search(preg,request.json.get('password'))):
            pw_hash = bcrypt.generate_password_hash(request.json.get("password"))
            user.password = pw_hash
        else:
            return "Invalid password format", 400
        #Ask for everything else
        user.firstname = request.json.get("firstname")
        user.lastname = request.json.get("lastname")
        
        db.session.add(user)

        db.session.commit()

        return jsonify({"success": True}), 201 




if __name__ == "__main__":
    Manager.run()
