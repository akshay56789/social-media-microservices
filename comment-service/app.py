import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt

from database import db, init_db
from models import Comment

app = Flask(__name__)
CORS(app)

# Configurations
JWT_SECRET = os.environ.get("JWT_SECRET", "dev_secret_key_change_me_in_prod")
AUTH_SERVICE_URL = os.environ.get("AUTH_SERVICE_URL", "http://auth-service")

# Initialize DB
init_db(app)

def decode_token(token):
    """Decodes JWT to retrieve the user ID."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload['sub']
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

def get_auth_user_id():
    """Extracts and verifies JWT token from Authorization header, returning userId."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ")[1]
    return decode_token(token)

def enrich_comments_with_user_details(comments):
    """Enriches comments with user details by calling internal auth-service."""
    enriched_comments = []
    user_cache = {}

    for comment in comments:
        comment_dict = comment.to_dict()
        user_id = comment.userId

        if user_id not in user_cache:
            try:
                response = requests.get(f"{AUTH_SERVICE_URL}/users/{user_id}", timeout=2)
                if response.status_code == 200:
                    user_cache[user_id] = response.json()
                else:
                    user_cache[user_id] = None
            except Exception as e:
                print(f"Error communicating with Auth Service at {AUTH_SERVICE_URL}: {e}")
                user_cache[user_id] = None

        user_info = user_cache[user_id]
        if user_info:
            comment_dict["author"] = {
                "username": user_info.get("username"),
                "profileImageUrl": user_info.get("profileImageUrl")
            }
        else:
            comment_dict["author"] = {
                "username": f"User #{user_id}",
                "profileImageUrl": ""
            }
        enriched_comments.append(comment_dict)

    return enriched_comments

# Endpoints
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Kubernetes liveness/readiness probes."""
    return jsonify({"status": "healthy", "service": "comment-service"}), 200

@app.route('/', methods=['POST'])
def add_comment():
    """Endpoint to add a comment to a post."""
    user_id = get_auth_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json() or {}
    post_id = data.get("postId")
    comment_text = data.get("commentText")

    if not post_id or not comment_text:
        return jsonify({"error": "Missing required fields (postId, commentText)"}), 400

    try:
        new_comment = Comment(
            postId=post_id,
            userId=user_id,
            commentText=comment_text
        )
        db.session.add(new_comment)
        db.session.commit()
        
        # Enrich the newly created comment for instant frontend updates
        enriched = enrich_comments_with_user_details([new_comment])[0]
        return jsonify({
            "message": "Comment added successfully",
            "comment": enriched
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Database error occurred: {str(e)}"}), 500

@app.route('/<int:post_id>', methods=['GET'])
def get_comments(post_id):
    """Endpoint to fetch all comments for a specific post."""
    try:
        comments = Comment.query.filter_by(postId=post_id).order_by(Comment.createdDate.asc()).all()
        enriched = enrich_comments_with_user_details(comments)
        return jsonify(enriched), 200
    except Exception as e:
        return jsonify({"error": f"Database error occurred: {str(e)}"}), 500

@app.route('/<int:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    """Endpoint to delete a comment."""
    user_id = get_auth_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    comment = Comment.query.get(comment_id)
    if not comment:
        return jsonify({"error": "Comment not found"}), 404

    # Ensure the user deleting is the author
    if comment.userId != user_id:
        return jsonify({"error": "Forbidden: You cannot delete someone else's comment"}), 403

    try:
        db.session.delete(comment)
        db.session.commit()
        return jsonify({"message": "Comment deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Database error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5003))
    app.run(host="0.0.0.0", port=port, debug=True)
