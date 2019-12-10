from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


class User(db.Model):
    __tablename__="user"
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    firstname = db.Column(db.String(150), nullable=False)
    lastname = db.Column(db.String(150), nullable=False)

    def __repr__(self):
        return "<User %r>" % self.email
    
    def serialize(self):
        return{
            "id": self.id,
            "email": self.email,
            "firstname": self.firstname,
            "lastname": self.lastname
        }
