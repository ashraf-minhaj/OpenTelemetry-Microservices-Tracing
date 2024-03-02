from flask import Flask, jsonify
app = Flask(__name__)

SERVICE_ONE_URL = 'http://localhost:5002'  # Replace with the actual URL of the database service

@app.route('/api/fetch_data', methods=['GET'])
def fetch_data():
    # Call the database service to get data
    data = {'name': 'Arif'}
    return jsonify({'result': data})

if __name__ == '__main__':
    app.run(port=5001, debug=True)
