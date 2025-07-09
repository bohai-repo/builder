#!/usr/bin/python3
import json, requests, os, utils
from flask import Flask, Response, request, jsonify
from clickhouse_pool import ChPool
from datetime import datetime, UTC
import pytz
import logging
import hashlib
import os


logging.basicConfig(level=getattr(logging, utils.LOG_LEVEL), format='%(asctime)s - %(levelname)s - %(message)s')
pool = ChPool(
    host=utils.CK_HOST,
    port=utils.CK_PORT,
    user=utils.CK_USER,
    password=utils.CK_PASSWORD,
    database=utils.CK_DATABASE,
    connections_min=5,
    connections_max=100,
)

MSG_TOKEN = utils.MSG_TOKEN
MSG_TYPE = utils.MSG_TYPE
DEFAULT_AT = utils.DEFAULT_AT
ALERTMANAGER_EXTURL = utils.ALERTMANAGER_EXTURL
PROM_K8S_TAG_KEY = utils.PROM_K8S_TAG_KEY


def wecom(webhook, content, at):
    webhook = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=' + webhook
    headers = {'Content-Type': 'application/json'}
    params = {'msgtype': 'markdown', 'markdown': {'content': f"{content}<@{at}>"}}
    data = bytes(json.dumps(params), 'utf-8')
    response = requests.post(webhook, headers=headers, data=data)
    print(f'【wecom】{response.json()}', flush=True)


def dingding(webhook, content, at):
    webhook = 'https://oapi.dingtalk.com/robot/send?access_token=' + webhook
    headers = {'Content-Type': 'application/json'}
    params = {"msgtype": "markdown", "markdown": {"title": "告警", "text": content}, "at": {"atMobiles": [at]}}
    data = bytes(json.dumps(params), 'utf-8')
    response = requests.post(webhook, headers=headers, data=data)
    print(f'【dingding】{response.json()}', flush=True)


def feishu(webhook, content, at):
    title = "告警通知"
    webhook = f'https://open.feishu.cn/open-apis/bot/v2/hook/{webhook}'
    headers = {'Content-Type': 'application/json'}
    params = {
        "msg_type": "interactive",
        "card": {
            "header": {"title": {"tag": "plain_text", "content": title}, "template": "red"},
            "elements": [
                {
                    "tag": "markdown",
                    "content": f"{content}\n<at id={at}></at>",
                }
            ],
        },
    }
    data = json.dumps(params)
    response = requests.post(webhook, headers=headers, data=data)
    print(f'【feishu】{response.json()}')


def parse_alert_time(time_str):
    """将Alertmanager的时间字符串转换为上海时区的DateTime对象"""
    time_str = time_str[:19] + 'Z'
    utc_time = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%SZ")
    utc_time = utc_time.replace(tzinfo=pytz.UTC)
    return utc_time.astimezone(pytz.timezone('Asia/Shanghai'))


def process_single_alert(alert):
    try:
        # 解析时间
        starts_at = parse_alert_time(alert['startsAt'])
        ends_at = parse_alert_time(alert['endsAt'])

        # 格式化时间字符串
        start_time_str = starts_at.strftime("%Y-%m-%d %H:%M:%S")
        end_time_str = ends_at.strftime("%Y-%m-%d %H:%M:%S")

        # 解析标签和注解
        labels = alert.get('labels', {})
        annotations = alert.get('annotations', {})
        description = annotations.get('description', '').split('\n- ')[-1]
        # 生成指纹
        fingerprint_str = labels[PROM_K8S_TAG_KEY] + labels['namespace'] + labels['pod'] + labels['alertname']
        fingerprint = hashlib.md5(fingerprint_str.encode(encoding='UTF-8')).hexdigest()
        promfinger = alert['fingerprint']

        alert_data = {
            'promfinger': promfinger,
            'fingerprint': fingerprint,
            'start_time': start_time_str,
            'end_time': end_time_str,
            'severity': labels.get('severity', ''),
            'alert_group': labels.get('alertgroup', ''),
            'alert_name': labels.get('alertname', ''),
            'env': labels.get(PROM_K8S_TAG_KEY, ''),
            'namespace': labels.get('namespace', ''),
            'container': labels.get('container', ''),
            'pod': labels.get('pod', ''),
            'description': description,
        }
        send_resolved = False if labels.get('send_resolved', True) == 'false' else True

        if alert['status'] == 'firing':
            handle_firing_alert(alert_data, send_resolved)
        else:
            handle_resolved_alert(alert_data, send_resolved)

    except Exception as e:
        logging.error(f"处理告警失败: {str(e)}", exc_info=True)


def handle_firing_alert(alert_data, send_resolved):
    check_query = f"""
        SELECT 1 FROM kubedoor.k8s_pod_alert_days
        WHERE toDate(start_time) = '{alert_data['start_time'].split()[0]}' and 
        fingerprint = '{alert_data['fingerprint']}'
        LIMIT 1
    """

    with pool.get_client() as client:
        existing = client.execute(check_query)

    if existing:
        # 获取当前时间并格式化为字符串
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        update_query = f"""
            ALTER TABLE kubedoor.k8s_pod_alert_days
            UPDATE count_firing = count_firing + 1, end_time = '{current_time}', 
            alert_status = 'firing', operate = '未处理', description = '{alert_data['description']}'
            WHERE toDate(start_time) = '{alert_data['start_time'].split()[0]}' and 
            fingerprint = '{alert_data['fingerprint']}'
        """

        with pool.get_client() as client:
            client.execute(update_query)
        logging.info(f"更新告警计数: {alert_data['fingerprint']}: {alert_data['alert_name']}")
    else:
        # 插入新记录
        count_resolved = 0 if send_resolved else -1
        insert_query = f"""
            INSERT INTO kubedoor.k8s_pod_alert_days (
                fingerprint, alert_status, send_resolved, operate, 
                start_time,count_firing,count_resolved,
                severity, alert_group, alert_name,
                env, namespace,
                container, pod, description
            ) VALUES (
                '{alert_data['fingerprint']}', 'firing', {send_resolved}, '未处理',
                '{alert_data['start_time']}', 1, {count_resolved},
                '{alert_data['severity']}', '{alert_data['alert_group']}', '{alert_data['alert_name']}',
                '{alert_data['env']}', '{alert_data['namespace']}',
                '{alert_data['container']}', '{alert_data['pod']}', '{alert_data['description']}'
            )
        """
        with pool.get_client() as client:
            client.execute(insert_query)
        logging.info(f"新建告警记录: {alert_data['fingerprint']}: {alert_data['alert_name']}")


def handle_resolved_alert(alert_data, send_resolved):
    if not send_resolved:
        logging.warning(f"告警 {alert_data['fingerprint']}: {alert_data['alert_name']} 的 send_resolved 为 false，不入库")
        return

    check_query = f"""
        SELECT 1 FROM kubedoor.k8s_pod_alert_days
        WHERE toDate(start_time) = '{alert_data['start_time'].split()[0]}' and fingerprint = '{alert_data['fingerprint']}'
        LIMIT 1
    """
    with pool.get_client() as client:
        existing = client.execute(check_query)

    if existing:
        update_query = f"""
            ALTER TABLE kubedoor.k8s_pod_alert_days
            UPDATE alert_status = 'resolved', end_time = '{alert_data['end_time']}', 
            count_resolved = count_resolved + 1, description = '{alert_data['description']}'
            WHERE toDate(start_time) = '{alert_data['start_time'].split()[0]}' AND 
            fingerprint = '{alert_data['fingerprint']}'
        """
        with pool.get_client() as client:
            client.execute(update_query)

        logging.info(f"标记告警解决: {alert_data['fingerprint']}: {alert_data['alert_name']}")
    else:
        logging.error(f"未找到对应告警记录: {alert_data['fingerprint']}: {alert_data['alert_name']}")


app = Flask(__name__)


@app.route('/clickhouse', methods=['POST'])
def handle_alert():
    try:
        data = request.get_json()
        if not data or 'alerts' not in data:
            return jsonify({'status': 'error', 'message': '无效的请求格式'}), 400

        for alert in data['alerts']:
            logging.debug(str(alert))
            process_single_alert(alert)

        return jsonify({'status': 'success', 'message': '告警处理完成'}), 200

    except Exception as e:
        logging.error(f"处理请求时发生异常: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route("/msg/<token>", methods=['POST'])
def alertnode(token):
    req = request.get_json()
    print('↓↓↓↓↓↓↓↓↓↓↓↓↓↓node↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓', flush=True)
    print(json.dumps(req, indent=2, ensure_ascii=False), flush=True)
    print('↑↑↑↑↑↑↑↑↑↑↑↑↑↑node↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑', flush=True)
    now_utc = datetime.now(UTC).replace(tzinfo=None)
    now_cn = datetime.now()

    # time1830 = datetime.strptime(str(now_cn.date()) + '18:30', '%Y-%m-%d%H:%M')
    # time0830 = datetime.strptime(str(now_cn.date()) + '08:30', '%Y-%m-%d%H:%M')

    # if (now_cn > time1830 or now_cn < time0830):
    #    return Response(status=204)
    allmd = ''
    for i in req["alerts"]:
        status = "故障" if i['status'] == "firing" else "恢复"
        try:
            firstime = datetime.strptime(i['startsAt'], '%Y-%m-%dT%H:%M:%SZ')
            durn_s = (now_utc - firstime).total_seconds()
        except:
            try:
                firstime = datetime.strptime(i['startsAt'], '%Y-%m-%dT%H:%M:%S.%fZ')
                durn_s = (now_utc - firstime).total_seconds()
            except:
                firstime = datetime.strptime(i['startsAt'].split(".")[0], '%Y-%m-%dT%H:%M:%S+08:00')
                durn_s = (now_cn - firstime).total_seconds()
        if durn_s < 60:
            durninfo = '小于1分钟'
        elif durn_s < 3600:
            durn = round(durn_s / 60, 1)
            durninfo = f"已持续{durn}分钟"
        else:
            durn = round(durn_s / 3600, 1)
            durninfo = f"已持续{durn}小时"

        summary = f"{i['labels']['alertname']},{durninfo}"
        message = i['annotations']['description']
        at = i['annotations'].get('at', DEFAULT_AT)

        url = f"{ALERTMANAGER_EXTURL}/#/alerts?silenced=false&inhibited=false&active=true&filter=%7Balertname%3D%22{i['labels']['alertname']}%22%7D"

        if status == '恢复':
            info = f"### {status}<font color=\"#6aa84f\">{summary}</font>\n- {message}\n\n"
        else:
            info = f"### {status}<font color=\"#ff0000\">{summary}</font>\n- {message}[【屏蔽】]({url})\n\n"
        allmd = allmd + info

    im, key = token.split('=', 1)
    if im == 'wecom':
        wecom(key, allmd, at)
    elif im == 'dingding':
        dingding(key, allmd, at)
    elif im == 'feishu':
        feishu(key, allmd, at)
    return Response(status=200)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
