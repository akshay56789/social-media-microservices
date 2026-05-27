from datetime import datetime
from database import db

class Post(db.Model):
    __tablename__ = 'posts'

    postId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userId = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    imageUrl = db.Column(db.String(500), nullable=True)
    createdDate = db.Column(db.DateTime, default=datetime.utcnow)

    # Establish relationship to Likes for easy querying (optional but very nice)
    likes = db.relationship('Like', backref='post', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "postId": self.postId,
            "userId": self.userId,
            "content": self.content,
            "imageUrl": self.imageUrl,
            "createdDate": self.createdDate.isoformat(),
            "likesCount": len(self.likes)
        }

class Like(db.Model):
    __tablename__ = 'likes'

    likeId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    postId = db.Column(db.Integer, db.ForeignKey('posts.postId'), nullable=False)
    userId = db.Column(db.Integer, nullable=False)
    createdDate = db.Column(db.DateTime, default=datetime.utcnow)
