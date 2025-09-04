import pytest
from flaskr.db import get_db

def test_index(client, auth):
    auth.login()
    response = client.get('/task/')
    assert b'Logout' in response.data
    assert b'test title' in response.data
    assert b'em 2025-09-02' in response.data
    assert b'test\nbody' in response.data
    assert b'href="/task/1/update"' in response.data

@pytest.mark.parametrize('path', (
    '/task/create',
    '/task/1/update',
    '/task/1/delete'
))
def test_login_required(client, path):
    response = client.post(path)
    assert response.headers["Location"] == "/auth/login"

def test_author_required(app, client, auth):
    with app.app_context():
        db = get_db()
        db.execute('UPDATE task SET author_id = 2 WHERE id = 1')
        db.commit()

    auth.login()
    assert client.post('/task/1/update').status_code == 403
    assert client.post('/task/1/delete').status_code == 403
    assert b'href="/task/1/update"' not in client.get('/task').data

@pytest.mark.parametrize('path', (
    '/task/2/update',
    '/task/2/delete'
))
def test_exists_required(client, auth, path):
    auth.login()
    assert client.post(path).status_code == 404


def test_create(client, auth, app):
    auth.login()
    assert client.get('/task/create').status_code == 200
    client.post('/task/create', data={'title': 'created', 'body': ''})

    with app.app_context():
        db = get_db()
        count = db.execute('SELECT COUNT(id) FROM task').fetchone()[0]
        assert count == 2

def test_update(client, auth, app):
    auth.login()
    assert client.get('/task/1/update').status_code == 200
    client.post('/task/1/update', data={'title': 'updated', 'body': ''})

    with app.app_context():
        db = get_db()
        task = db.execute('SELECT * FROM task WHERE id = 1').fetchone()
        assert task['title'] == 'updated'   

@pytest.mark.parametrize('path', (
    '/task/create',
    '/task/1/update'
))
def test_create_update_validate(client, auth, path):
    auth.login()
    response = client.post(path, data={'title': '', 'body': ''})
    assert b'Titulo e obrigatorio' in response.data

def test_delete(client, auth, app):
    auth.login()
    response = client.post('/task/1/delete')
    assert response.headers["Location"] == "/task/"
    
    with app.app_context():
        db = get_db()
        task = db.execute('SELECT * FROM task WHERE id = 1').fetchone()
        assert task is None
