from flask import Flask, jsonify
import requests

app = Flask(__name__)

SERVICE_TWO_URL = 'http://localhost:5001'  # Replace with the actual URL of service_two

@app.route('/api/get_data', methods=['GET'])
def get_data():
    # Call service_two to fetch data
    response_from_service_two = requests.get(f'{SERVICE_TWO_URL}/api/fetch_data')

    # Process the data or perform additional tasks if needed
    processed_data = f"Processed data from service_two: {response_from_service_two.json()}"

    return jsonify({'result': processed_data})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
