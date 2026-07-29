import pytest

from app import app


@pytest.fixture
def client():
    app.config.update(TESTING=True)
    with app.test_client() as client:
        yield client


def test_register_routes_open_the_registration_form(client):
    response = client.get('/register', follow_redirects=False)
    assert response.status_code == 302
    assert response.headers['Location'].endswith('/auth/register')

    response = client.get('/auth/register', follow_redirects=False)
    assert response.status_code == 200
    assert b'Create Your Account' in response.data


def test_invalid_login_does_not_crash(client):
    response = client.post('/auth/login', data={'login_input': 'unknown@example.com', 'password': 'wrongpass'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid email, phone, or password.' in response.data


def test_feature_routes_require_login_for_anonymous_users(client):
    for path in ['/technologies/', '/market/prices', '/schemes/', '/community/']:
        response = client.get(path, follow_redirects=False)
        assert response.status_code == 302
        assert response.headers['Location'].endswith('/auth/login')
