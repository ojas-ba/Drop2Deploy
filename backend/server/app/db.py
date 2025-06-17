import sqlite3

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            uid TEXT PRIMARY KEY,
            email TEXT,
            name TEXT,
            picture TEXT,
            provider TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS models (
            model_id INTEGER PRIMARY KEY AUTOINCREMENT,
            uid TEXT NOT NULL,
            name TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_type TEXT NOT NULL,
            deployment_status BOOLEAN NOT NULL DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (uid) REFERENCES users(uid) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def close_db_connection(conn):
    if conn:
        conn.close()

def create_user(uid, email, name, picture, provider):
    connection = get_db_connection()
    cursor = connection.cursor()
    id = cursor.execute('''
        INSERT INTO users (uid, email, name, picture, provider)
        VALUES (?, ?, ?, ?, ?)
    ''', (uid, email, name, picture, provider))
    connection.commit()
    close_db_connection(connection)

def create_model(uid, name, file_path, file_type):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('''
        INSERT INTO models (uid, name, file_path, file_type)
        VALUES (?, ?, ?, ?)
    ''', (uid, name, file_path, file_type))
    connection.commit()
    close_db_connection(connection)

def delete_model(model_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('''
        DELETE FROM models WHERE model_id = ?
    ''', (model_id,))
    connection.commit()
    close_db_connection(connection)

def get_models_by_user(uid):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('''
        SELECT * FROM models WHERE uid = ?
    ''', (uid,))
    models = cursor.fetchall()
    models = [dict(model) for model in models]
    close_db_connection(connection)
    return models

def get_models_by_deployment_status(deployment_status):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('''
        SELECT * FROM models WHERE deployment_status = ?
    ''', (deployment_status,))
    models = cursor.fetchall()
    models = [dict(model) for model in models]
    close_db_connection(connection)
    return models