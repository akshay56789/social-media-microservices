import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt

from database import db, init_db
from models import Post, Like

app = Flask(__name__)
CORS(app)

# Configurations
JWT_SECRET = os.environ.get("JWT_SECRET", "dev_secret_key_change_me_in_prod")
AUTH_SERVICE_URL = os.environ.get("AUTH_SERVICE_URL", "http://auth-service")

# Initialize DB
init_db(app)

def decode_token(token):
    """Decodes the JWT token to extract the user ID."""
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

def enrich_posts_with_user_details(posts):
    """
    Enriches posts with user details by calling the auth-service API.
    This demonstrates internal service-to-service communication.
    """
    enriched_posts = []
    user_cache = {}  # Prevent multiple HTTP calls for the same user in a single request

    for post in posts:
        post_dict = post.to_dict()
        user_id = post.userId
        
        if user_id not in user_cache:
            try:
                # Call internal service using K8s DNS or local environment URL
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
            post_dict["author"] = {
                "username": user_info.get("username"),
                "profileImageUrl": user_info.get("profileImageUrl"),
                "bio": user_info.get("bio")
            }
        else:
            post_dict["author"] = {
                "username": f"User #{user_id}",
                "profileImageUrl": "",
                "bio": "Profile information unavailable"
            }
        enriched_posts.append(post_dict)
    
    return enriched_posts

# Endpoints
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Kubernetes liveness/readiness probes."""
    return jsonify({"status": "healthy", "service": "post-service"}), 200

@app.route('/', methods=['POST'])
def create_post():
    """Endpoint to create a new social media post."""
    user_id = get_auth_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json() or {}
    content = data.get("content")
    image_url = data.get("imageUrl", "")

    if not content:
        return jsonify({"error": "Content is required for creating a post"}), 400

    try:
        new_post = Post(
            userId=user_id,
            content=content,
            imageUrl=image_url
        )
        db.session.add(new_post)
        db.session.commit()
        return jsonify({
            "message": "Post created successfully",
            "post": new_post.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Database error occurred: {str(e)}"}), 500

@app.route('/', methods=['GET'])
def get_posts():
    """Endpoint to retrieve all posts, enriched with user information."""
    try:
        # Retrieve posts sorted by date in descending order
        posts = Post.query.order_by(Post.createdDate.desc()).all()
        # Enrich posts with user details
        enriched = enrich_posts_with_user_details(posts)
        return jsonify(enriched), 200
    except Exception as e:
        return jsonify({"error": f"Error fetching posts: {str(e)}"}), 500

@app.route('/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    """Endpoint to delete a post."""
    user_id = get_auth_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    post = Post.query.get(post_id)
    if not post:
        return jsonify({"error": "Post not found"}), 404

    # Ensure the user deleting the post is the creator of the post
    if post.userId != user_id:
        return jsonify({"error": "Forbidden: You cannot delete someone else's post"}), 403

    try:
        db.session.delete(post)
        db.session.commit()
        return jsonify({"message": "Post deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Database error occurred: {str(e)}"}), 500

@app.route('/<int:post_id>/like', methods=['POST'])
def toggle_like(post_id):
    """Endpoint to like or unlike a post."""
    user_id = get_auth_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    post = Post.query.get(post_id)
    if not post:
        return jsonify({"error": "Post not found"}), 404

    # Check if user already liked the post
    existing_like = Like.query.filter_by(postId=post_id, userId=user_id).first()

    try:
        if existing_like:
            # Unlike
            db.session.delete(existing_like)
            message = "Post unliked successfully"
        else:
            # Like
            new_like = Like(postId=post_id, userId=user_id)
            db.session.add(new_like)
            message = "Post liked successfully"

        db.session.commit()
        return jsonify({
            "message": message,
            "likesCount": Like.query.filter_by(postId=post_id).count()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Database error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5002))
    app.run(host="0.0.0.0", port=port, debug=True)
