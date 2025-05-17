import mysql.connector
from mysql.connector import Error
from flask import current_app, g
import click
from flask.cli import with_appcontext

def get_db():
    if 'db' not in g:
        try:
            g.db = mysql.connector.connect(
                host=current_app.config['OB_HOST'],
                port=current_app.config['OB_PORT'],
                user=current_app.config['OB_USER'],
                password=current_app.config['OB_PASSWORD'],
                database=current_app.config['OB_DATABASE']
            )
            current_app.logger.info(f"Successfully connected to OceanBase: {current_app.config['OB_DATABASE']}")
        except Error as e:
            current_app.logger.error(f"Error connecting to OceanBase: {e}")
            raise  # Re-raise the exception to be handled by the caller or Flask
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
        current_app.logger.info(f"Database connection closed.")

def init_db():
    """Clear existing data and create new tables."""
    db = get_db()
    cursor = db.cursor()
    # 在 tests/data/init_db.sql 中定义表结构
    # 这里为了简单，直接写SQL，实际项目中应从文件读取
    # 注意：OceanBase MySQL 模式下，表名和字段名大小写敏感（取决于配置，但最好保持一致）
    # 确保你的 init_db.sql 文件路径正确
    sql_file_path = os.path.join(os.path.dirname(__file__), '..', 'tests', 'data', 'init_db.sql')
    if not os.path.exists(sql_file_path):
        current_app.logger.warning(f"SQL init file not found at {sql_file_path}. Skipping DB initialization from file.")
        # Fallback or error
        # For now, let's define very basic tables here if file not found, for demonstration
        # This part should ideally always load from init_db.sql
        cursor.execute("DROP TABLE IF EXISTS papers;")
        cursor.execute("DROP TABLE IF EXISTS users;")
        cursor.execute("""
            CREATE TABLE users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(80) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        cursor.execute("""
            CREATE TABLE papers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                authors VARCHAR(500),
                abstract TEXT,
                keywords VARCHAR(500),
                publication_year INT,
                user_id INT,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        current_app.logger.info("Initialized database with inline schema (SQL file preferred).")
    else:
        with open(sql_file_path, 'r') as f:
            sql_script = f.read()
        # MySQL Connector's cursor.execute() typically doesn't support multiple statements directly
        # separated by ';'. You might need to split them or use a library that handles this,
        # or execute them one by one. For simplicity, we assume init_db.sql contains statements
        # that can be run sequentially or a single multi-statement block if the driver supports it.
        # A robust solution would parse and execute statements individually.
        # For now, let's try executing them as a whole block; this might fail with some drivers/setups
        # if there are multiple statements.
        # A better way for mysql.connector is to iterate:
        for statement in sql_script.split(';'):
            if statement.strip(): # ignore empty statements
                try:
                    cursor.execute(statement)
                except Error as e:
                    current_app.logger.error(f"Error executing statement: {statement[:50]}... - {e}")
                    # Decide if you want to stop or continue on error
        current_app.logger.info("Initialized the database from SQL file.")
    
    db.commit()
    cursor.close()

@click.command('init-db')
@with_appcontext
def init_db_command():
    """CLI command to initialize the database."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    """Register database functions with the Flask app."""
    app.teardown_appcontext(close_db) # Call close_db when app context ends
    app.cli.add_command(init_db_command) # Add "flask init-db" command

# Helper for executing queries (optional, but good practice)
def query_db(query, args=(), one=False, commit=False):
    db = get_db()
    cursor = db.cursor(dictionary=True) # dictionary=True returns rows as dicts
    try:
        cursor.execute(query, args)
        if commit:
            db.commit()
            # For INSERT, UPDATE, DELETE, might return lastrowid or rowcount
            return cursor.lastrowid if cursor.lastrowid else cursor.rowcount
        
        rv = cursor.fetchall()
        return (rv[0] if rv else None) if one else rv
    except Error as e:
        db.rollback() # Rollback on error
        current_app.logger.error(f"Database query error: {e} on query: {query[:100]}...")
        raise # Re-raise for higher level handling
    finally:
        cursor.close()

import os # ensure os is imported for path operations