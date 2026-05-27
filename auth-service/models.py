from datetime import datetime
from database import db

class User(db.Model):
    __tablename__ = 'users'

    userId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    passwordHash = db.Column(db.String(255), nullable=False)
    profileImageUrl = db.Column(db.String(500), nullable=True)
    bio = db.Column(db.String(500), nullable=True)
    createdDate = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "userId": self.userId,
            "username": self.username,
            "email": self.email,
            "profileImageUrl": self.profileImageUrl,
            "bio": self.bio,
            "createdDate": self.createdDate.isoformat()
        }
