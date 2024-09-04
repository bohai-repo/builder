import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

wrest_url = os.environ.get('wrest_url') or 'http://127.0.0.1:7600'

@app.route('/api', methods=['POST'])
def api():
    # 接收方
    receiver = request.args.get('receiver', '47719964397@chatroom')
    
    title = request.form.get('title')
    desp = request.form.get('desp')
    link = request.form.get('link')
    task_id = request.form.get('task_id')
    task_title = request.form.get('task_title')

    if not title or not desp or not link or not task_id or not task_title:
        return jsonify({'error': 'Missing one or more required parameters'}), 400

    url = f'{wrest_url}/wcf/send_txt'
    headers = {'Content-Type': 'application/json;charset=utf-8'}
    payload = {
        "receiver": receiver,
        "msg": f"{task_title}的更新: {title}\t文章地址: {link}"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return jsonify({'status': 'success', 'response': response.json()})
    except requests.exceptions.RequestException as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(port=8872, host='0.0.0.0')