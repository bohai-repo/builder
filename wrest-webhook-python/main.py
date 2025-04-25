import os
import re
import sqlite3
import logging
import requests
from openai import OpenAI, OpenAIError
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

webhook_database_file = './data/data.db'
ai_api_key = os.environ.get('ai_api_key') or 'xxxxx'
ai_api_enable = os.environ.get('ai_api_enable') or 'false'
wrest_url = os.environ.get('wrest_url') or 'http://127.0.0.1:7600'

logging.basicConfig(level=logging.INFO, format='%(asctime)s  %(levelname)s  %(message)s')
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

def summarize_text(text,link):
    if not text:
        pass
    try:
        api_key = os.getenv("ai_api_key")
        if not api_key:
            raise ValueError("未配置openai的api key,请在环境变量中配置ai_api_key")

        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个信息提取总结的助手，我需要你对我给你的信息进行分析和总结，并返回简短的、150字以内的总结.如果你发现内容里包含媒体文件地址(图片或视频)，那么请将媒体文件的地址输出，格式为: 包含x张图片/视频 (换行符) 图片/视频地址: xxxxx (请点击查看)"},
                {"role": "user", "content": text},
            ],
            stream=False
        )

        return response.choices[0].message.content

    except (OpenAIError, ValueError) as e:
        logger.error(f"分析内容: {link} 出错,错误原因: {e}")

@app.route('/', methods=['GET'])
def api_ui():
    return send_from_directory('static', 'index.html')

@app.route('/api', methods=['POST', 'GET'])
def api():
    # param receiver string 消息接收人，wxid 或者 roomid
    receiver = request.args.get('receiver', '47719964397@chatroom')
    # 处理从RssPush发送过来的Post请求
    if request.method == 'POST':
        title = request.form.get('title')
        desp = request.form.get('desp')
        link = request.form.get('link')
        task_id = request.form.get('task_id')
        task_title = request.form.get('task_title')

        if not title or not link or not task_id or not task_title:
            return jsonify({'status': 'fail', 'msg': 'no param'}), 400

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
            return jsonify({'status': 'fail', 'msg': 'duplicate'})
        else:
            if ai_api_enable:
                summary = summarize_text(desp,link)
                msg = f"{task_title}：{title}\n\n{link} \n\n\nAi总结(deepseek): {summary}"
            else:
                msg = f"{task_title}：{title}\n\n{link}"
            insert_message(task_title, title, link, summary)

    # 处理直接请求的消息发送
    elif request.method == 'GET':
        msg = request.args.get('msg')
        img = request.args.get('img')
        file = request.args.get('file')
        wechat_id = request.args.get('wechat_id')

        if not msg and not img and not file:
            return jsonify({'status': 'fail', 'msg': 'need param values {file} or {msg} or {img}'}), 400

    # param msg string 要发送的消息，\n使用 `\\\\n` （单杠）；如果 @ 人的话，需要带上跟 `aters` 里数量相同的 @
    url = f'{wrest_url}/wcf/send_txt'
    headers = {'Content-Type': 'application/json;charset=utf-8'}
    payload = {
        "receiver": receiver,
        "msg": msg
    }

    # param wechat_id string 要 @ 的 wxid，多个用逗号分隔；`@所有人` 只需要 `notify@all`
    if 'wechat_id' in request.args:
        payload = {
            "receiver": receiver,
            "msg": f"{msg}",
            "aters": [
                wechat_id
            ]
        }

    # 发送图片，非线程安全
    # param path string 图片路径，如：`C:/Projs/WeChatRobot/TEQuant.jpeg` 或 url，如：`http://xxx.com/xxx.png`
    # param receiver string 消息接收人，wxid 或者 roomid
    if 'img' in request.args:
        payload = {
            "receiver": receiver,
            "path": f"{img}",
        }
        url = f'{wrest_url}/wcf/send_img'

    # 发送文件，非线程安全
    # param path string 本地文件路径，如：`C:/Projs/WeChatRobot/README.MD` 或 url，如：`http://xxx.com/xxx.zip`
    # param receiver string 消息接收人，wxid 或者 roomid
    if 'file' in request.args:
        payload = {
            "receiver": receiver,
            "path": f"{file}",
        }
        url = f'{wrest_url}/wcf/send_file'

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return jsonify({'status': 'success'})
    except requests.exceptions.RequestException as e:
        logger.error(f"{e}")
        return jsonify({'status': 'fail', 'message': "system is busy,please try again later."}), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=False, host='0.0.0.0', port=8872)
