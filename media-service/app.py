import os
import uuid
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# Configurations
PORT = int(os.environ.get("PORT", 5004))
UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "uploads")
AZURE_STORAGE_CONN = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER_NAME = os.environ.get("AZURE_STORAGE_CONTAINER", "social-media-images")

# Ensure local upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize Azure Blob Service Client if connection string is provided
blob_service_client = None
azure_enabled = False

if AZURE_STORAGE_CONN:
    try:
        from azure.storage.blob import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONN)
        # Create container if it doesn't exist
        container_client = blob_service_client.get_container_client(CONTAINER_NAME)
        if not container_client.exists():
            container_client.create_container(public_access='blob')
        azure_enabled = True
        print(f"Azure Blob Storage initialized successfully. Using container: {CONTAINER_NAME}")
    except Exception as e:
        print(f"Failed to initialize Azure Blob Storage ({e}). Falling back to local storage.")

# Helper to validate file extension
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Endpoints
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Kubernetes liveness/readiness probes."""
    storage_type = "Azure Blob Storage" if azure_enabled else "Local Storage Fallback"
    return jsonify({
        "status": "healthy",
        "service": "media-service",
        "storage": storage_type
    }), 200

@app.route('/upload', methods=['POST'])
def upload_file():
    """Endpoint to upload a file."""
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected for upload"}), 400

    if not file or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Allowed: png, jpg, jpeg, gif"}), 400

    # Generate unique filename to avoid naming collisions
    ext = file.filename.rsplit('.', 1)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}.{ext}"

    if azure_enabled:
        try:
            blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=unique_filename)
            # Set content type header so the browser renders instead of downloading
            content_type = f"image/{ext}" if ext != 'jpg' else 'image/jpeg'
            
            blob_client.upload_blob(file.read(), content_type=content_type)
            # Retrieve the public URL
            file_url = blob_client.url
            return jsonify({
                "message": "File uploaded successfully to Azure Blob Storage",
                "imageUrl": file_url,
                "filename": unique_filename
            }), 201
        except Exception as e:
            print(f"Error uploading to Azure Blob Storage: {e}")
            return jsonify({"error": f"Azure upload failed: {str(e)}"}), 500
    else:
        # Fallback: Save file to local folder
        try:
            filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
            file.save(filepath)
            
            # Construct a relative API path that goes through the API gateway/ingress
            file_url = f"/api/media/uploads/{unique_filename}"
            return jsonify({
                "message": "File uploaded successfully to local storage",
                "imageUrl": file_url,
                "filename": unique_filename
            }), 201
        except Exception as e:
            print(f"Error saving file locally: {e}")
            return jsonify({"error": f"Local upload failed: {str(e)}"}), 500

@app.route('/uploads/<filename>', methods=['GET'])
def serve_uploaded_file(filename):
    """Serve files stored locally (fallback mode)."""
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/media/<filename>', methods=['DELETE'])
def delete_file(filename):
    """Endpoint to delete an uploaded file."""
    filename = secure_filename(filename)
    if azure_enabled:
        try:
            blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=filename)
            if blob_client.exists():
                blob_client.delete_blob()
                return jsonify({"message": f"Blob {filename} deleted successfully from Azure"}), 200
            else:
                return jsonify({"error": "Blob not found"}), 404
        except Exception as e:
            return jsonify({"error": f"Azure delete failed: {str(e)}"}), 500
    else:
        # Local Delete
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                return jsonify({"message": f"File {filename} deleted successfully from local storage"}), 200
            except Exception as e:
                return jsonify({"error": f"Local file deletion failed: {str(e)}"}), 500
        else:
            return jsonify({"error": "File not found"}), 404

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=PORT, debug=True)
