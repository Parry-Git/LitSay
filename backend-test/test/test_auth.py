import json

def test_register_user(client, init_database): # init_database fixture ensures clean DB
    """Test user registration."""
    response = client.post('/api/auth/register', json={
        'username': 'testuser1',
        'email': 'test1@example.com',
        'password': 'password123'
    })
    assert response.status_code == 201
    assert response.json['message'] == 'User registered successfully'

    # Test duplicate username
    response = client.post('/api/auth/register', json={
        'username': 'testuser1',
        'email': 'test2@example.com',
        'password': 'password123'
    })
    assert response.status_code == 409 # Conflict
    assert 'Username already exists' in response.json['message']

def test_login_user(client, init_database):
    """Test user login."""
    # Register user first
    client.post('/api/auth/register', json={
        'username': 'loginuser',
        'email': 'login@example.com',
        'password': 'password123'
    })

    # Test successful login
    response = client.post('/api/auth/login', json={
        'username': 'loginuser',
        'password': 'password123'
    })
    assert response.status_code == 200
    assert 'token' in response.json
    assert response.json['user']['username'] == 'loginuser'

    # Test login with wrong password
    response = client.post('/api/auth/login', json={
        'username': 'loginuser',
        'password': 'wrongpassword'
    })
    assert response.status_code == 401
    assert 'Invalid username or password' in response.json['message']

def test_get_me(client, init_database, auth_headers): # Use auth_headers fixture
    """Test getting current user info with token."""
    response = client.get('/api/auth/me', headers=auth_headers)
    assert response.status_code == 200
    assert response.json['username'] == 'testuser_auth' # from auth_headers fixture
    assert response.json['email'] == 'testuser_auth@example.com'

def test_get_me_no_token(client, init_database):
    response = client.get('/api/auth/me')
    assert response.status_code == 401
    assert 'Token is missing' in response.json['message']