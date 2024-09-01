import os
import requests
from flask import Flask, request, jsonify


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

wrest_url = os.environ.get('wrest_url') or 'http://127.0.0.1:7600'

@app.route('/api', methods=['GET'])
def api():
    receiver = request.args.get('receiver')
    msg = request.args.get('msg')

    if not receiver or not msg:
        return jsonify({'error': 'Missing receiver or msg parameters'}), 400

    url = f'{wrest_url}/wcf/send_txt'
    headers = {'Content-Type': 'application/json;charset=utf-8'}
    payload = {
        "receiver": receiver,
        "msg": msg
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return jsonify({'status': 'success', 'response': response.json()})
    except requests.exceptions.RequestException as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(port=8872,host='0.0.0.0')