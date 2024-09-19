import os
import re
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

wrest_url = os.environ.get('wrest_url') or 'http://127.0.0.1:7600'

@app.route('/api', methods=['POST', 'GET'])
def api():
    # 消息接收方
    receiver = request.args.get('receiver', '47719964397@chatroom')
    
    # 处理从RssPush发送过来的Post请求
    if request.method == 'POST':
        title = request.form.get('title')
        desp = request.form.get('desp')
        link = request.form.get('link')
        task_id = request.form.get('task_id')
        task_title = request.form.get('task_title')

        if not title or not desp or not link or not task_id or not task_title:
            return jsonify({'error': 'Missing one or more required parameters'}), 400
        link = [re.sub(r'/en/', '/', link)]
        # 优化来源标题
        if task_title == 'V2EX-programmer':
            task_title = 'v2ex-程序员'
        elif task_title == 'V2EX-qna':
            task_title = 'v2ex-问与答'
        elif task_title == 'yuyao-101210404未来三天天气':
            task_title = '余姚未来三天天气'
        elif task_title == 'yuyao-101210404实时天气':
            task_title = '余姚实时天气'
        elif task_title == 'pudong-101020600实时天气':
            task_title = '浦东实时天气'
        elif task_title == 'Kubernetes' and 'v2ex' in link:
            task_title = 'v2ex-k8s'
        msg = f"{task_title}：{title}\n\n{link}"
    # 处理直接请求的消息发送
    elif request.method == 'GET':
        msg = request.args.get('msg')
        if not msg:
            return jsonify({'error': 'Missing "msg" parameter'}), 400

    url = f'{wrest_url}/wcf/send_txt'
    headers = {'Content-Type': 'application/json;charset=utf-8'}
    payload = {
        "receiver": receiver,
        "msg": msg
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return jsonify({'status': 'success', 'response': response.json()})
    except requests.exceptions.RequestException as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(port=8872, host='0.0.0.0')