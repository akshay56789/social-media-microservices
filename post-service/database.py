import os
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    db_conn = os.environ.get("DB_CONNECTION_STRING")
    
    if not db_conn:
        # Use absolute path in /app/data/ so the Docker volume only persists DB files,
        # not the entire /app directory (which would overwrite code on rebuilds)
        os.makedirs("/app/data", exist_ok=True)
        db_conn = "sqlite:////app/data/post.db"
        print("WARNING: DB_CONNECTION_STRING not set. Falling back to local SQLite: " + db_conn)
    else:
        if db_conn.startswith("Driver="):
            import urllib
            params = urllib.parse.quote_plus(db_conn)
            db_conn = f"mssql+pyodbc:///?odbc_connect={params}"
        print("Connecting to SQL Server database...")

    app.config["SQLALCHEMY_DATABASE_URI"] = db_conn
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        print("Database tables initialized successfully.")
