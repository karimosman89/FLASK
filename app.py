from flask import Flask, request, jsonify, make_response
from random import uniform
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd

app = Flask(__name__)

# Load credentials from CSV
credentials = pd.read_csv("credentials.csv")

# Helper function to check user permissions
def check_permissions(username, password):
    user = credentials[(credentials['username'] == username) & (credentials['password'] == password)]
    if len(user) == 0:
        return None
    return user.iloc[0]['v1'], user.iloc[0]['v2']

@app.route('/status', methods=['GET'])
def api_status():
    return "1"

@app.route('/welcome', methods=['GET'])
def welcome():
    username = request.args.get('username')
    return f"Welcome, {username}!"

@app.route('/permissions', methods=['POST'])
def permissions():
    auth_header = request.headers.get('Authorization')
    if auth_header is None:
        return make_response(jsonify({"error": "Authorization header is missing"}), 401)

    username, password = auth_header.split('=')
    permissions = check_permissions(username, password)
    if permissions is None:
        return make_response(jsonify({"error": "Invalid credentials"}), 401)

    response = {
        "username": username,
        "v1": permissions[0],
        "v2": permissions[1]
    }
    return jsonify(response)

@app.route('/v1/sentiment', methods=['POST'])
def v1_sentiment():
    auth_header = request.headers.get('Authorization')
    if auth_header is None:
        return make_response(jsonify({"error": "Authorization header is missing"}), 401)

    username, password = auth_header.split('=')
    permissions = check_permissions(username, password)
    if permissions is None or permissions[0] != 1:
        return make_response(jsonify({"error": "Unauthorized access or model not available"}), 403)

    sentiment_score = uniform(-1, 1)
    return jsonify({"sentiment_score": sentiment_score})

@app.route('/v2/sentiment', methods=['POST'])
def v2_sentiment():
    auth_header = request.headers.get('Authorization')
    if auth_header is None:
        return make_response(jsonify({"error": "Authorization header is missing"}), 401)

    username, password = auth_header.split('=')
    permissions = check_permissions(username, password)
    if permissions is None or permissions[1] != 1:
        return make_response(jsonify({"error": "Unauthorized access or model not available"}), 403)

    sentence = request.form.get('sentence')
    if sentence is None:
        return make_response(jsonify({"error": "Sentence not provided"}), 400)

    analyzer = SentimentIntensityAnalyzer()
    vs = analyzer.polarity_scores(sentence)
    return jsonify({"sentiment_score": vs['compound']})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=2222)
