import os
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
import bcrypt
import jwt

from database import db, init_db
from models import User

app = Flask(__name__)
# Enable CORS so frontend or other services can communicate with it
CORS(app)

# Configurations
JWT_SECRET = os.environ.get("JWT_SECRET", "dev_secret_key_change_me_in_prod")
JWT_EXPIRATION_HOURS = 24

# Initialize DB
init_db(app)

def generate_token(user_id):
    """Generates a JWT token for the user."""
    payload = {
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        'iat': datetime.utcnow(),
        'sub': user_id
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

def decode_token(token):
    """Decodes the JWT token and returns user_id, or None if invalid."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload['sub']
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

# Endpoints
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Kubernetes liveness/readiness probes."""
    return jsonify({"status": "healthy", "service": "auth-service"}), 200

@app.route('/register', methods=['POST'])
def register():
    """Endpoint to register a new user."""
    data = request.get_json() or {}
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    profile_image_url = data.get("profileImageUrl", "")
    bio = data.get("bio", "")

    if not username or not email or not password:
        return jsonify({"error": "Missing required fields (username, email, password)"}), 400

    # Check if user already exists
    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({"error": "Username or Email already registered"}), 409

    # Hash the password
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    try:
        new_user = User(
            username=username,
            email=email,
            passwordHash=password_hash,
            profileImageUrl=profile_image_url,
            bio=bio
        )
        db.session.add(new_user)
        db.session.commit()
        
        token = generate_token(new_user.userId)
        return jsonify({
            "message": "User registered successfully",
            "token": token,
            "user": new_user.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Database error occurred: {str(e)}"}), 500

@app.route('/login', methods=['POST'])
def login():
    """Endpoint to authenticate a user and retrieve a JWT."""
    data = request.get_json() or {}
    email_or_username = data.get("email") or data.get("username")
    password = data.get("password")

    if not email_or_username or not password:
        return jsonify({"error": "Missing email/username or password"}), 400

    # Search by email or username
    user = User.query.filter((User.email == email_or_username) | (User.username == email_or_username)).first()

    if not user or not bcrypt.checkpw(password.encode('utf-8'), user.passwordHash.encode('utf-8')):
        return jsonify({"error": "Invalid email/username or password"}), 401

    token = generate_token(user.userId)
    return jsonify({
        "message": "Login successful",
        "token": token,
        "user": user.to_dict()
    }), 200

@app.route('/profile', methods=['GET'])
def profile():
    """Endpoint to fetch details of the logged in user."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing or invalid authorization header"}), 401

    token = auth_header.split(" ")[1]
    user_id = decode_token(token)

    if not user_id:
        return jsonify({"error": "Token is invalid or expired"}), 401

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify(user.to_dict()), 200

# Utility endpoint to fetch user profiles by a list/single ID (used by post-service or comment-service to enrich data)
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user_by_id(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.to_dict()), 200

if __name__ == '__main__':
    # Running locally
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=True)
