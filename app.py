from flask import Flask, request, render_template, jsonify, make_response
import requests
import sqlite3

app = Flask(__name__)
WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"
WEATHER_API_PARAMS = {
    'daily': 'temperature_2m_max,temperature_2m_min',
    'current_weather': 'true',
    'timezone': 'auto'
}


# Инициализация базы данных SQLite
def init_db():
    with sqlite3.connect("weather_app.db") as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS search_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )"""
        )


init_db()


# Получение координат города через Nominatim
def get_coordinates(city):
    try:
        geocoding_url = f"https://nominatim.openstreetmap.org/search?q={city}&format=json"
        geocoding_response = requests.get(geocoding_url).json()
        if len(geocoding_response) == 0:
            return None
        return geocoding_response[0]['lat'], geocoding_response[0]['lon']
    except requests.exceptions.RequestException as e:
        print(f"Error fetching geocoding data: {e}")
        return None


# Получение данных о погоде с API Open-Meteo
def fetch_weather(latitude, longitude):
    try:
        params = WEATHER_API_PARAMS.copy()
        params.update({'latitude': latitude, 'longitude': longitude})
        weather_response = requests.get(WEATHER_API_URL, params=params)
        weather_response.raise_for_status()
        return weather_response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None


@app.route('/')
def index():
    last_city = request.cookies.get('last_city')  # Получаем последний введенный город из cookies
    return render_template('index.html', last_city=last_city)


@app.route('/weather', methods=['POST'])
def weather():
    city = request.form['city']  # Получаем название города из формы
    coordinates = get_coordinates(city)  # Получаем координаты города
    if coordinates is None:
        return render_template('error.html', message="Error fetching geocoding data.")

    latitude, longitude = coordinates
    weather_data = fetch_weather(latitude, longitude)  # Получаем данные о погоде

    if weather_data is None:
        return render_template('error.html', message="Error fetching weather data.")

    # Сохраняем запрос в историю поиска
    with sqlite3.connect("weather_app.db") as conn:
        conn.execute("INSERT INTO search_history (city) VALUES (?)", (city,))

    # Создаем ответ с куками, чтобы сохранить последний введенный город
    resp = make_response(render_template('weather.html', weather=weather_data, city=city))
    resp.set_cookie('last_city', city)
    return resp


@app.route('/history')
def history():
    # Получаем историю поиска из базы данных
    with sqlite3.connect("weather_app.db") as conn:
        cur = conn.cursor()
        cur.execute("SELECT city, COUNT(city) FROM search_history GROUP BY city")
        history_data = cur.fetchall()
    return jsonify(history_data)  # Возвращаем историю в формате JSON


if __name__ == '__main__':
    app.run(debug=True)  # Запуск приложения Flask в режиме отладки
