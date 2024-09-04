import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

wrest_url = os.environ.get('wrest_url') or 'http://127.0.0.1:7600'

@app.route('/api/<receiver>', methods=['POST'])
def api(receiver):
    # Extract form data
    title = request.form.get('title')
    desp = request.form.get('desp')
    link = request.form.get('link')
    task_id = request.form.get('task_id')
    task_title = request.form.get('task_title')

    if not receiver or not title or not desp or not link or not task_id or not task_title:
        return jsonify({'error': 'Missing one or more parameters'}), 400

    # Prepare payload for the downstream API
    url = f'{wrest_url}/wcf/send_txt'
    headers = {'Content-Type': 'application/json;charset=utf-8'}
    payload = {
        "receiver": receiver,
        "title": title,
        "desp": desp,
        "link": link,
        "task_id": task_id,
        "task_title": task_title
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return jsonify({'status': 'success', 'response': response.json()})
    except requests.exceptions.RequestException as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(port=8872, host='0.0.0.0')