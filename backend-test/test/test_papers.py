import json

def test_add_paper_unauthorized(client, init_database):
    response = client.post('/api/papers', json={'title': 'Test Paper'})
    assert response.status_code == 401 # Unauthorized, token missing

def test_add_and_get_paper(client, init_database, auth_headers):
    """Test adding a paper and then retrieving it."""
    # Add a paper
    paper_data = {
        'title': 'My Awesome Paper',
        'authors': 'Dr. Test, Prof. Example',
        'abstract': 'This is a revolutionary paper.',
        'keywords': 'test, example, awesome',
        'publication_year': 2023
    }
    response = client.post('/api/papers', json=paper_data, headers=auth_headers)
    assert response.status_code == 201
    assert 'paper_id' in response.json
    paper_id = response.json['paper_id']

    # Get the paper by ID
    response_get = client.get(f'/api/papers/{paper_id}', headers=auth_headers)
    assert response_get.status_code == 200
    retrieved_paper = response_get.json
    assert retrieved_paper['title'] == paper_data['title']
    assert retrieved_paper['authors'] == paper_data['authors']

    # Get all papers (should include the one we added)
    response_list = client.get('/api/papers', headers=auth_headers)
    assert response_list.status_code == 200
    papers_list = response_list.json
    assert any(p['id'] == paper_id and p['title'] == paper_data['title'] for p in papers_list)

def test_search_papers(client, init_database, auth_headers):
    # Add some papers
    client.post('/api/papers', json={'title': 'Alpha Research', 'keywords': 'alpha, study'}, headers=auth_headers)
    client.post('/api/papers', json={'title': 'Beta Findings', 'keywords': 'beta, report'}, headers=auth_headers)
    client.post('/api/papers', json={'title': 'Another Alpha Study', 'keywords': 'alpha, project'}, headers=auth_headers)

    # Search for 'alpha'
    response = client.get('/api/papers?q=alpha', headers=auth_headers)
    assert response.status_code == 200
    results = response.json
    assert len(results) == 2 # Should find 'Alpha Research' and 'Another Alpha Study'
    for paper in results:
        assert 'alpha' in paper['title'].lower() or 'alpha' in paper.get('keywords','').lower()

    # Search for 'beta'
    response_beta = client.get('/api/papers?q=beta', headers=auth_headers)
    assert response_beta.status_code == 200
    results_beta = response_beta.json
    assert len(results_beta) == 1
    assert 'beta' in results_beta[0]['title'].lower()