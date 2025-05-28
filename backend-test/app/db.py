import mysql.connector
from mysql.connector import Error
from flask import current_app, g
import click
from flask.cli import with_appcontext
import os

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
            current_app.logger.info(f"Successfully connected: {current_app.config['OB_DATABASE']}")
        except Error as e:
            current_app.logger.error(f"Error when connecting: {e}")
            raise
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
        current_app.logger.info(f"Database connection closed.")

def init_db():
    db = get_db()
    cursor = db.cursor()

    sql_file_path = os.path.join(os.path.dirname(__file__), 'utils/paperdb_initv1.sql')
    if not os.path.exists(sql_file_path):
        raise FileNotFoundError(f"SQL file not found at {sql_file_path}")
    with open(sql_file_path, 'r') as sql_file:
        sql_script = sql_file.read()
    for statement in sql_script.split(';'):
        if statement.strip():
            try:
                cursor.execute(statement)
            except Error as e:
                current_app.logger.error(f"Error executing statement: {statement[:50]}... - {e}")
    db.commit()
    cursor.close()
    current_app.logger.info("Initialized the database from SQL file.")


@click.command('init-db')
@with_appcontext
def init_db_command():
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


def query_db(query, args=(), one=False, commit=False):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    try:
        cursor.execute(query, args)
        if commit:
            db.commit()
            return cursor.lastrowid if cursor.lastrowid else cursor.rowcount
        else:
            result = cursor.fetchall()
            return (result[0] if result else None) if one else result

    except Error as e:
        db.rollback()
        current_app.logger.error(f"Error executing query: {query[:100]} Error: {e}")
        raise
    finally:
        cursor.close()




