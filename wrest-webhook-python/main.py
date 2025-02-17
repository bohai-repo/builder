import os
import re
import sqlite3
import logging
import requests
from openai import OpenAI, OpenAIError
from flask import Flask, request, jsonify

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

webhook_database_file = '/app/data/data.db'
ai_api_key = os.environ.get('ai_api_key') or 'xxxxx'
ai_api_enable = os.environ.get('ai_api_enable') or 'false'
wrest_url = os.environ.get('wrest_url') or 'http://127.0.0.1:7600'

logging.basicConfig(filename='/app/data/main.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_db_connection():
    conn = sqlite3.connect(webhook_database_file)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS webhook_message_push (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_title TEXT NOT NULL,
                title TEXT NOT NULL,
                link TEXT,
                summary TEXT,
                UNIQUE (link)
            )
        ''')
        conn.commit()


def check_duplicate(link):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM webhook_message_push WHERE link = ?", (link,)) # 修改SQL查询语句
        result = cursor.fetchone()
        if result:
            logger.info(f"推送跳过,重复推送：{link}")
        return result is not None


def insert_message(task_title, title, link, summary):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO webhook_message_push (task_title, title, link, summary) VALUES (?, ?, ?, ?)",
                           (task_title, title, link, summary))
            conn.commit()
        except sqlite3.IntegrityError:
            pass

def summarize_text(text):
    if not text:
        return "获取的文章描述为空,无法进行总结。"
    try:
        api_key = os.getenv("ai_api_key")
        if not api_key:
            raise ValueError("未配置openai的api key,请在环境变量中配置ai_api_key")

        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个信息提取总结的助手，我需要你对我给你的信息进行分析和总结，并返回简短的、150字以内的总结，此外我还需要通过你爆粗口说脏话来表达总结"},
                {"role": "user", "content": text},
            ],
            stream=False
        )

        return response.choices[0].message.content

    except (OpenAIError, ValueError) as e:
        return "系统繁忙,请稍后再试"

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

        if not title or not link or not task_id or not task_title:
            return jsonify({'error': '缺少必要参数'}), 400

        link = re.sub(r'/en/', '/', link)
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
        elif task_title == 'luoyang-101180901实时天气':
            task_title = '洛阳实时天气'
        elif task_title == 'Kubernetes' and 'v2ex' in link:
            task_title = 'v2ex-k8s'

        # 检测重复消息
        if check_duplicate(link):
            return jsonify({'status': 'skip', 'msg': '重复推送'})
        else:
            if ai_api_enable:
                summary = summarize_text(desp)
                msg = f"{task_title}：{title}\n\n{link} \n\n\nAi总结(deepseek): {summary}"
            else:
                msg = f"{task_title}：{title}\n\n{link}"
            insert_message(task_title, title, link, summary)

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
    init_db()
    app.run(port=8872, host='0.0.0.0')