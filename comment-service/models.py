from datetime import datetime
from database import db

class Comment(db.Model):
    __tablename__ = 'comments'

    commentId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    postId = db.Column(db.Integer, nullable=False)
    userId = db.Column(db.Integer, nullable=False)
    commentText = db.Column(db.Text, nullable=False)
    createdDate = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "commentId": self.commentId,
            "postId": self.postId,
            "userId": self.userId,
            "commentText": self.commentText,
            "createdDate": self.createdDate.isoformat()
        }
