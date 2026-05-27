import os
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    # Retrieve the database connection string from environment variables
    # If not set, fallback to a local SQLite database for ease of local testing
    db_conn = os.environ.get("DB_CONNECTION_STRING")
    
    if not db_conn:
        # Use absolute path in /app/data/ so the Docker volume only persists DB files
        os.makedirs("/app/data", exist_ok=True)
        db_conn = "sqlite:////app/data/auth.db"
        print("WARNING: DB_CONNECTION_STRING not set. Falling back to local SQLite: " + db_conn)
    else:
        # Check if it starts with standard driver names or needs standard prefixing
        # E.g., if it's an Azure SQL string, SQLAlchemy requires the pyodbc dialect:
        # mssql+pyodbc://...
        if db_conn.startswith("Driver="):
            # Convert ODBC connection string to SQLAlchemy compatible format
            import urllib
            params = urllib.parse.quote_plus(db_conn)
            db_conn = f"mssql+pyodbc:///?odbc_connect={params}"
        print("Connecting to SQL Server database...")

    app.config["SQLALCHEMY_DATABASE_URI"] = db_conn
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    db.init_app(app)
    
    with app.app_context():
        # Ensure all tables are created
        db.create_all()
        print("Database tables initialized successfully.")
