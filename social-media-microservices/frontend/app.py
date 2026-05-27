import os
from flask import Flask, render_template, jsonify

app = Flask(__name__)

# Endpoints to serve standard HTML templates
@app.route('/')
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/feed')
def feed():
    return render_template('feed.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/create-post')
def create_post():
    return render_template('create_post.html')

# Health Check for Kubernetes
@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "service": "frontend"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
