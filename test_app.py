import pytest
from app import app, init_db


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client


def test_index(client):
    rv = client.get('/')
    assert rv.status_code == 200
    assert b'Weather App' in rv.data


def test_fetch_weather(client, monkeypatch):
    def mock_get_coordinates(city):
        return (55.7558, 37.6173)  # Координаты Москвы

    def mock_fetch_weather(latitude, longitude):
        return {
            "current_weather": {"temperature": 20},
            "daily": [
                {"date": "2024-07-23", "temperature_2m_max": 25, "temperature_2m_min": 15},
                {"date": "2024-07-24", "temperature_2m_max": 24, "temperature_2m_min": 14}
            ]
        }

    monkeypatch.setattr('app.get_coordinates', mock_get_coordinates)
    monkeypatch.setattr('app.fetch_weather', mock_fetch_weather)

    rv = client.post('/weather', data={'city': 'Moscow'})
    assert rv.status_code == 200
    assert b'Moscow' in rv.data


def test_history(client):
    rv = client.get('/history')
    assert rv.status_code == 200
