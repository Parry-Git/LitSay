import pytest
import os
from app import create_app
from app.db import init_db, get_db, close_db

@pytest.fixture(scope='session') # Use session scope for app factory if config doesn't change
def app():
    """Create and configure a new app instance for each test session."""
    # Set a fixed secret key for testing if not already set by TestingConfig
    os.environ['SECRET_KEY'] = 'test_secret_key'
    os.environ['JWT_SECRET_KEY'] = 'test_jwt_secret_key'
    # Point to a test database if needed, or ensure init_db clears it
    # Make sure TestingConfig in app/config.py uses a test database name
    # e.g., by setting OB_DATABASE = 'test_paperdb'
    
    app = create_app('testing') # Use the 'testing' configuration

    # Establish an application context before running the tests.
    with app.app_context():
        # You might want to drop and re-create tables for each test session or module
        # init_db() # Initialize the database (creates tables)
        pass # init_db will be called explicitly where needed or by a specific fixture

    yield app

    # Clean up after tests if necessary (e.g., drop test database)
    # with app.app_context():
    #     db = get_db()
    #     cursor = db.cursor()
    #     cursor.execute("DROP DATABASE IF EXISTS " + app.config['OB_DATABASE']) # Careful with this!
    #     cursor.close()


@pytest.fixture()
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture()
def runner(app):
    """A test runner for CLI commands."""
    return app.test_cli_runner()

@pytest.fixture(scope='function') # Re-init DB for each test function for isolation
def init_database(app):
    with app.app_context():
        init_db() # This will run your app/db.py init_db function
    yield # This is where the testing happens
    # Optional: Clean up specific tables or data after each test if init_db doesn't fully reset
    # For example, if init_db only creates tables but doesn't clear them
    # with app.app_context():
    #     db = get_db()
    #     cursor = db.cursor()
    #     cursor.execute("DELETE FROM papers;")
    #     cursor.execute("DELETE FROM users;")
    #     db.commit()
    #     cursor.close()

@pytest.fixture
def auth_headers(client):
    """Fixture to get auth headers after logging in a test user."""
    # First, register a user (or assume one exists from init_database)
    client.post('/api/auth/register', json={
        'username': 'testuser_auth',
        'email': 'testuser_auth@example.com',
        'password': 'password123'
    })
    # Login
    response = client.post('/api/auth/login', json={
        'username': 'testuser_auth',
        'password': 'password123'
    })
    assert response.status_code == 200
    token = response.get_json()['token']
    return {
        'Authorization': f'Bearer {token}'
    }