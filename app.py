from flask import Flask,request, json, jsonify, render_template, redirect, url_for, session
import requests
import json
import os
import random
import mysql.connector

app = Flask(__name__, static_url_path='/static')
app.secret_key = 'your_secret_key'  # Required for session management

# Constants for database connection
DB_HOST = "buh89x1pi8cgvaw4161i-mysql.services.clever-cloud.com"
DB_USER = "ucwyejivetooukiz"
DB_PASSWORD = "aAo8DieytbUo0FiYV4RY"
DB_NAME = "buh89x1pi8cgvaw4161i"

INITIAL_BALANCE = 3000

# Function to connect to the database
def connect_to_db():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )


API_KEY = 'rxS3WOVB7zNbC0kvfLtpljJVa6lAqoIZpoqsytwU'
REQUEST_ID = 'YOUR_REQUEST_ID'

# Route to serve the main index page
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    # Retrieve inputs using request.form
    destination1 = request.form.get('destination1')
    destination2 = request.form.get('destination2')
    return f"<h1>Destination 1: {destination1}, Destination 2: {destination2}</h1>"

@app.route('/search', methods=['POST'])
def search():
    search_query = request.form.get('search_query')
    return f"<h1>You searched for: {search_query}</h1>"


@app.route('/get_route', methods=['POST'])
def get_route():
    # Get the data from the frontend (origin and destination)
    data = request.get_json()
    origin = data.get('origin')
    destination = data.get('destination')

    if not origin or not destination:
        return jsonify({'error': 'Origin and destination are required'}), 400

    try:
        # Parse the origin and destination coordinates (format: latitude,longitude)
        origin_lat, origin_lng = map(float, origin.split(','))
        destination_lat, destination_lng = map(float, destination.split(','))

        # Build the API request URL for the Ola Maps routing API
        url = f'https://api.olamaps.io/routing/v1/directions/basic?origin={origin_lat},{origin_lng}&destination={destination_lat},{destination_lng}&api_key={API_KEY}'

        # Make the API request to Ola Maps
        response = requests.post(url, headers={'X-Request-Id': REQUEST_ID})
        response_data = response.json()

        if 'routes' not in response_data or len(response_data['routes']) == 0:
            return jsonify({'error': 'No route found'}), 404

        # Extract route details from the API response
        route = response_data['routes'][0]
        distance = route['summary']['distance']
        duration = route['summary']['duration']
        steps = [step['instruction'] for step in route['legs'][0]['steps']]

        # Prepare the data to be written into a JSON file
        route_info = {
            'distance': distance,
            'duration': duration,
            'steps': steps
        }

        # Ensure the directory exists
        os.makedirs(os.path.join(app.root_path, 'static/js'), exist_ok=True)

        # Write the output to a JSON file (static/js/route.json)
        with open(os.path.join(app.root_path, 'static/js/route.json'), 'w') as json_file:
            json.dump(route_info, json_file, indent=4)

        # Return a success message
        return jsonify({'message': 'Route information saved to static/js/route.json'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Route for login page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        password = request.form['password']
        dob = request.form['dob']
        balance = INITIAL_BALANCE

        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO abc (phone, name, password, dob, balance) VALUES (%s, %s, %s, %s, %s)",
            (phone, name, password, dob, balance)
        )
        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('shop', phone=phone))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']

        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM abc WHERE phone = %s", (phone,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and user[2] == password:
            return redirect(url_for('shop', phone=phone))
        else:
            return "Invalid credentials. Please try again."

    return render_template('login.html')


# Route for the map page
@app.route('/map')
def map():
    return render_template('map.html')

# Route for the busgroup page
@app.route('/busgroup')
def busgroup():
    return render_template('busgroup.html')

# Route for the busradio page
@app.route('/busradio')
def busradio():
    return render_template('busradio.html')

# Route for the afterlog page (tiles.html)
@app.route('/afterlog')
def afterlog():
    return render_template('afterlog/tiles.html')

@app.route('/ui')
def ui():
    return render_template('ui.html')

# Route for the need help page
@app.route('/needhelp')
def needhelp():
    return render_template('needhelp.html')



# API route to serve the coordinates from JSON
@app.route('/api/coordinates')
def get_coordinates():
    with open('data/coordinates.json') as f:
        data = f.read()
    return jsonify(data)

# Additional API routes for other data files if needed
@app.route('/api/themes')
def get_themes():
    with open('data/themes.json') as f:
        data = f.read()
    return jsonify(data)

@app.route('/api/darkmode')
def get_darkmode_styles():
    with open('data/dark-mode-style.json') as f:
        data = f.read()
    return jsonify(data)

# Running the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
