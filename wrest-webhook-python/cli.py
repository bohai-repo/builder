import requests
import argparse
from urllib.parse import quote


def send_wechat_message():
    parser = argparse.ArgumentParser(description='发送微信消息')
    parser.add_argument('--receiver', required=True, help='接收者ID/群ID')
    parser.add_argument('--msg', required=True, help='要发送的消息内容')
    parser.add_argument('--wechat_id', required=True, help='微信用户ID')
    parser.add_argument('--host', default='127.0.0.1', help='服务器主机地址')
    parser.add_argument('--port', default=8872, type=int, help='服务器端口号')

    args = parser.parse_args()

    # 构造请求URL
    base_url = f"http://{args.host}:{args.port}/api"
    params = {
        "receiver": quote(args.receiver),
        "msg": quote(args.msg),
        "wechat_id": quote(args.wechat_id)
    }
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    url = f"{base_url}?{query_string}"

    print(f"Sending request to: {url}")

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        print(f"发送成功！响应内容：{response.text}")
    except requests.exceptions.RequestException as e:
        print(f"请求失败：{str(e)}")


if __name__ == "__main__":
    send_wechat_message()