import os
import sys
import time
import json
import requests
from datetime import datetime, timedelta
from collections import defaultdict
from clickhouse_driver import Client
from clickhouse_driver.errors import ServerException
from functools import wraps
from loguru import logger

logger.remove()
logger.add(
    sys.stderr,
    format='<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> [<level>{level}</level>] <level>{message}</level>',
    level='INFO',
)


# 环境变量
CK_DATABASE = os.environ.get('CK_DATABASE')
CK_HOST = os.environ.get('CK_HOST')
CK_HTTP_PORT = os.environ.get('CK_HTTP_PORT')
CK_PASSWORD = os.environ.get('CK_PASSWORD')
CK_PORT = os.environ.get('CK_PORT')
CK_USER = os.environ.get('CK_USER')
MSG_TOKEN = os.environ.get('MSG_TOKEN')
MSG_TYPE = os.environ.get('MSG_TYPE')
PROM_K8S_TAG_KEY = os.environ.get('PROM_K8S_TAG_KEY')
PROM_TYPE = os.environ.get('PROM_TYPE')
PROM_URL = os.environ.get('PROM_URL')


ckclient = Client(
    host=CK_HOST,
    port=CK_PORT,
    user=CK_USER,
    password=CK_PASSWORD,
    database=CK_DATABASE,
)


def retry_on_exception(retries=3, delay=1, backoff=2):
    def decorator_retry(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            while attempt < retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempt += 1
                    logger.warning(f"尝试第 {attempt} 次遇到错误: {e}")
                    if attempt < retries:
                        time.sleep(delay * (backoff ** (attempt - 1)))
            raise Exception("达到最大重试次数，无数据可用")

        return wrapper

    return decorator_retry


@retry_on_exception()
def execute_query(query):
    return ckclient.execute(query)


query_list = [
    "pod_num",
    "core_usage",
    "core_usage_percent",
    "wss_usage_MB",
    "wss_usage_percent",
    "limit_core",
    "limit_mem_MB",
    "request_core",
    "request_mem_MB",
]
query_dict = {
    # pod数
    "pod_num": 'min_over_time(count(label_replace(kube_pod_container_info{{env}container!="",container!="POD",namespace=~"{namespace}"}, "deployment", "$1", "pod", "^(.*)-[a-z0-9]+-[a-z0-9]+$")) by({env_key}deployment,namespace)[{duration}:])',
    # 使用核数P95
    "core_usage": 'quantile_over_time(0.95, avg by ({env_key}namespace, deployment) (label_replace(irate(container_cpu_usage_seconds_total{{env}container!="",container!="POD",namespace=~"{namespace}"}[2m]),"deployment","$1","pod","^(.*)-[a-z0-9]+-[a-z0-9]+$"))[{duration}:])',
    # CPU使用率P95
    "core_usage_percent": 'quantile_over_time(0.95,(sum by ({env_key}namespace, deployment)(label_replace(irate(container_cpu_usage_seconds_total{{env}container!="",container!="POD",namespace=~"{namespace}"}[2m]),"deployment","$1","pod","^(.*)-[a-z0-9]+-[a-z0-9]+$"))/sum by ({env_key}namespace, deployment)(label_replace(container_spec_cpu_quota{{env}container!="",container!="POD",namespace=~"{namespace}"},"deployment","$1","pod","^(.*)-[a-z0-9]+-[a-z0-9]+$")/100000)*100)[{duration}:]) != Inf',
    # WSS内存使用MB P95
    "wss_usage_MB": 'quantile_over_time(0.95,avg by ({env_key}namespace, deployment)(label_replace(container_memory_working_set_bytes{{env}container!="",container!="POD",namespace=~"{namespace}"},"deployment","$1","pod","^(.*)-[a-z0-9]+-[a-z0-9]+$"))[{duration}:])/1024/1024',
    # WSS内存使用率P95
    "wss_usage_percent": 'quantile_over_time(0.95,avg by ({env_key}namespace, deployment)(label_replace(container_memory_working_set_bytes{{env}container!="",container!="POD",namespace=~"{namespace}"},"deployment","$1","pod","^(.*)-[a-z0-9]+-[a-z0-9]+$"))[{duration}:])/max(max_over_time(label_replace(kube_pod_container_resource_limits{{env}resource="memory",unit="byte",container!="",container!="POD",namespace=~"{namespace}"},"deployment","$1","pod","^(.*)-[a-z0-9]+-[a-z0-9]+$")[{duration}:])) by ({env_key}namespace,deployment) *100 != Inf',
    # CPU limit
    "limit_core": 'max(max_over_time(label_replace(kube_pod_container_resource_limits{{env}resource="cpu", unit="core",container!="",container!="POD",namespace=~"{namespace}"},"deployment","$1","pod","^(.*)-[a-z0-9]+-[a-z0-9]+$")[{duration}:])) by ({env_key}namespace,deployment) *1000',
    # 内存limit_MB
    "limit_mem_MB": 'max(max_over_time(label_replace(kube_pod_container_resource_limits{{env}resource="memory",unit="byte",container!="",container!="POD",namespace=~"{namespace}"},"deployment","$1","pod","^(.*)-[a-z0-9]+-[a-z0-9]+$")[{duration}:])) by ({env_key}namespace,deployment)/1024/1024',
    # CPU request
    "request_core": 'max(max_over_time(label_replace(kube_pod_container_resource_requests{{env}resource="cpu", unit="core",container!="",container!="POD",namespace=~"{namespace}"},"deployment","$1","pod","^(.*)-[a-z0-9]+-[a-z0-9]+$")[{duration}:])) by ({env_key}namespace,deployment) * 1000',
    # 内存request_MB
    "request_mem_MB": 'max(max_over_time(label_replace(kube_pod_container_resource_requests{{env}resource="memory", unit="byte",container!="",container!="POD",namespace=~"{namespace}"},"deployment","$1","pod","^(.*)-[a-z0-9]+-[a-z0-9]+$")[{duration}:])) by ({env_key}deployment,namespace)/1024/1024',
    # 查询节点的所有deployment列表
    "deployments_by_node": 'kube_pod_info{{env}created_by_kind="ReplicaSet", namespace!~"{namespace}", node="{node}"}'
}

namespace_str_exclude = "loggie|kubedoor|kube-otel|cert-manager|kube-system|ops-monit"


def calculate_peak_duration_and_end_time(peak_hours):
    # 提取开始和结束时间
    start_str, end_str = peak_hours.split('-')
    start_time = datetime.strptime(start_str, '%H:%M:%S')
    end_time = datetime.strptime(end_str, '%H:%M:%S')
    # 计算持续时间
    duration = end_time - start_time
    duration_hours = duration.seconds // 3600
    duration_minutes = (duration.seconds % 3600) // 60
    # 生成持续时间的字符串
    duration_str = f"{duration_hours}h{duration_minutes}m"

    start_time_part = start_time.time()
    end_time_part = end_time.time()
    return duration_str, start_time_part, end_time_part


def check_and_delete_day_data(date, env_value):
    """检查是否有当天的数据，有则删除"""
    query_sql = f"""select * from kubedoor.k8s_resources where date = '{date}' and env = '{env_value}'"""
    delete_sql = f"""delete from kubedoor.k8s_resources where date = '{date}' and env = '{env_value}'"""
    logger.info(f"query_sql==={query_sql}")
    result = ckclient.execute(query_sql)
    ckclient.disconnect()
    if result:
        logger.info(f"从表k8s_resources删除{env_value} {date}的数据")
        logger.info(f"delete_sql==={delete_sql}")
        ckclient.execute("SET allow_experimental_lightweight_delete = 1")
        ckclient.execute(delete_sql)
    return result


def get_prom_url():
    """按类型选择查询指标的方式"""
    # url = f"{PROM_URL}/api/v1/query_range"
    url = f"{PROM_URL}/api/v1/query"
    # if PROM_TYPE == "Prometheus":
    #     url = f"{PROM_URL}/api/v1/query_range"
    # if PROM_TYPE == "Victoria-Metrics-Single":
    #     url = f"{PROM_URL}/api/v1/query_range"
    # if PROM_TYPE == "Victoria-Metrics-Cluster":
    #     url = f"{PROM_URL}/select/0/prometheus/api/v1/query_range"
    return url


def fetch_prom_namespaces(env_value):
    # 使用 max_over_time 来获取最近一小时的数据
    # query = f'group by (namespace) (max_over_time(kube_namespace_created{{{PROM_K8S_TAG_KEY}="{env_value}"}}[1h]))'
    query = f'group by (namespace) (kube_namespace_created{{{PROM_K8S_TAG_KEY}="{env_value}"}})'
    try:
        response = requests.get(get_prom_url(), params={'query': query})
        response.raise_for_status()  # 检查请求是否成功
        data = response.json()
        namespaces = []
        for result in data['data']['result']:
            labels = result['metric']
            namespaces.append(labels.get('namespace'))
        return namespaces
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error fetching data from Prometheus: {e}")


def fetch_prom_envs():
    # query = f'group by ({PROM_K8S_TAG_KEY}) (kube_state_metrics_build_info)'
    query = f'group by ({PROM_K8S_TAG_KEY}) (kube_node_info)'
    try:
        response = requests.get(get_prom_url(), params={'query': query})
        response.raise_for_status()  # 检查请求是否成功
        data = response.json()
        envs = []
        for result in data['data']['result']:
            labels = result['metric']
            envs.append(labels.get(PROM_K8S_TAG_KEY))
        return envs
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error fetching data from Prometheus: {e}")


def get_prom_data(promql, env_key, env_value, namespace_str, start_time_full, end_time_full, duration):
    """获取指标源数据"""
    url = get_prom_url()
    if PROM_K8S_TAG_KEY:
        k8s_filter = f'{PROM_K8S_TAG_KEY}=~"{env_value}",'
        query = query_dict.get(promql).replace("{env}", k8s_filter).replace("{env_key}", f"{PROM_K8S_TAG_KEY},")
    else:
        query = query_dict.get(promql).replace("{env}", '').replace("{env_key}", '')
    query = query.replace("{namespace}", namespace_str).replace("{duration}", duration)
    # querystring = {"query":query,"start":start_time_full.timestamp(),"end":end_time_full.timestamp(),"step":"15"}
    querystring = {"query": query, "time": end_time_full.timestamp(), "step": "15"}
    logger.info(querystring)
    response = requests.request("GET", url, params=querystring).json()
    print(json.dumps(response), flush=True)
    if response.get("status") == "success":
        result = response["data"]["result"]
        metrics_dict = {}
        for x in result:
            # for tv in x['values']:
            #     if PROM_K8S_TAG_KEY:
            #         k8s = x['metric'][PROM_K8S_TAG_KEY]
            #     else:
            #         k8s = "k8s"
            #     ns = x['metric'].get('namespace',x['metric'].get('k8s_ns')) or x['metric'].get('namespace',x['metric'].get('destination_workload_namespace'))
            #     ms = x['metric'].get('deployment')
            #     if promql == "pod_num":
            #         metrics_dict[f'{tv[0]}@{k8s}@{ns}@{ms}'] = int(tv[1])
            #     else:
            #         metrics_dict[f'{tv[0]}@{k8s}@{ns}@{ms}'] = float(tv[1])

            if PROM_K8S_TAG_KEY:
                k8s = x['metric'][PROM_K8S_TAG_KEY]
            else:
                k8s = "k8s"
            ns = x['metric'].get('namespace', x['metric'].get('k8s_ns')) or x['metric'].get(
                'namespace', x['metric'].get('destination_workload_namespace')
            )
            ms = x['metric'].get('deployment')
            if promql == "pod_num":
                metrics_dict[f'{x["value"][0]}@{k8s}@{ns}@{ms}'] = int(x['value'][1])
            else:
                metrics_dict[f'{x["value"][0]}@{k8s}@{ns}@{ms}'] = float(x['value'][1])
        logger.info('单个指标数量 {}: {}', promql, len(metrics_dict))
        return metrics_dict
    else:
        logger.error('ERROR {} {}', promql, env_key)



def get_node_deployments(node, env_value):
    logger.info(f"开始查询节点 {node} 上的所有deployment (env: {env_value})")
    deployment_list = []
    url = get_prom_url()
    k8s_filter = f'{PROM_K8S_TAG_KEY}=~"{env_value}",'
    query = query_dict.get('deployments_by_node').replace("{env}", k8s_filter).replace("{namespace}", namespace_str_exclude).replace("{node}", node)
    querystring = {"query": query, "step": "15"}
    logger.info(f"查询参数: {querystring}")
    response = requests.request("GET", url, params=querystring).json()
    print(json.dumps(response), flush=True)
    if response.get("status") == "success":
        result = response["data"]["result"]
        logger.info(f"在节点 {node} 上找到 {len(result)} 个deployment")
        for x in result:
            ns = x['metric'].get('namespace', x['metric'].get('k8s_ns')) or x['metric'].get(
                'namespace', x['metric'].get('destination_workload_namespace')
            )
            pod = x['metric'].get('pod')
            deployment_list.append({
                "namespace": ns,
                "pod": pod
            })
        logger.info(f"节点 {node} 上的deployment列表: {json.dumps(deployment_list)}")
        return deployment_list
    else:
        logger.error(f'查询节点 {node} 上的deployment列表失败')


def merged_dict(env_key, env_value, namespace_str, duration_str, start_time_full, end_time_full):
    """解析指标源数据，处理成列表"""
    metrics_list = []
    metrics_keys_list = []
    k8s_metrics_list = []
    for promql in query_list:
        metrics_dict = get_prom_data(promql, env_key, env_value, namespace_str, start_time_full, end_time_full, duration_str)
        metrics_keys_list = metrics_keys_list + list(metrics_dict.keys())
        metrics_list.append(metrics_dict)
    metrics_keys_list = list(set(metrics_keys_list))
    new_metrics_list = []
    for i in metrics_list:
        for j in metrics_keys_list:
            if j not in i:
                i[j] = -1
        logger.info('处理完成后（补全查不到的值）的数据行数: {}', len(i))
        new_metrics_list.append(i)

    merged_dict = defaultdict(list)
    for d in new_metrics_list:
        for k, v in d.items():
            merged_dict[k].append(v)
    for k, v in merged_dict.items():
        key_list = k.split('@')
        key_list[0] = datetime.fromtimestamp(int(key_list[0]))
        if v[0] == -1:  # 如果未从指标查到pod数，则置为0
            v[0] = 0
        logger.info(key_list + v)
        k8s_metrics_list.append(key_list + v + [-1, -1, -1])
    return k8s_metrics_list


def metrics_to_ck(k8s_metrics_list):
    """将指标数据存入ck"""
    batch_size = 10000
    for i in range(0, len(k8s_metrics_list), batch_size):
        begin = time.time()
        batch_data = k8s_metrics_list[i : i + batch_size]
        try:
            ckclient.execute("INSERT INTO k8s_resources VALUES", batch_data)
            logger.info(
                f"🌊高峰期数据写入CK == count: insert batch {i//batch_size}",
                "耗时：{:.2f}s".format(time.time() - begin),
            )
        except ServerException as e:
            logger.exception("Failed to insert batch {}:// {}", i // batch_size, e)

    ckclient.disconnect()
    return True


def merge_dicts(dict1, dict2):
    merged_dict = dict1.copy()
    for key, value in dict2.items():
        if key in merged_dict:
            merged_dict[key].update(value)
        else:
            merged_dict[key] = value
    return merged_dict


def ck_optimize():
    result = ckclient.execute('OPTIMIZE TABLE k8s_res_control FINAL')
    return True


def ck_alter(sql):
    result = ckclient.execute(sql)
    return True


def ck_agent_collect_info():
    """从ck中读取agent的信息"""
    result = ckclient.execute('SELECT env, peak_hours FROM k8s_agent_status WHERE collect = 1')
    formatted_result = [list(row) for row in result]
    return formatted_result


def ck_init_agent_status(env):
    """从ck中读取agent的信息"""
    result = ckclient.execute(f"SELECT 1 FROM k8s_agent_status where env = '{env}'")
    if not result:
        ckclient.execute(f"INSERT INTO k8s_agent_status (env) VALUES ('{env}')")
    return True


def ck_agent_info():
    """从ck中读取agent的信息"""
    agent_info = {}
    try:
        rows = ckclient.execute("SELECT env, collect, peak_hours, admission, admission_namespace, nms_not_confirm, scheduler FROM k8s_agent_status")
        if rows:
            for row in rows:
                env = row[0]
                agent_info[env] = {
                    "collect": row[1],
                    "peak_hours": row[2],
                    "admission": row[3],
                    "admission_namespace": row[4],
                    "nms_not_confirm": row[5],
                    "scheduler": row[6],
                }

    except ServerException as e:
        logger.exception(e)
    ckclient.disconnect()
    return agent_info


def get_deploy_admis(env, namespace, deployment):
    """从ck中读取agent的信息"""
    try:
        result = ckclient.execute(
            f"""SELECT scheduler,nms_not_confirm FROM k8s_agent_status where env = '{env}' and admission = 1 and admission_namespace like '%"{namespace}"%'"""
        )
        if result:
            query = (
                f"SELECT pod_count, pod_count_ai, pod_count_manual, request_cpu_m, request_mem_mb, limit_cpu_m, limit_mem_mb "
                f"FROM k8s_res_control "
                f"WHERE env='{env}' AND namespace='{namespace}' "
                f"AND deployment='{deployment}'"
            )
            deploy_res = ckclient.execute(query)
            if deploy_res:
                deploy_res_list = list(deploy_res[0])
                deploy_res_list.append(result[0][0])  # scheduler
                logger.info(f"🔊master(admis)返回:【{env}】【{namespace}】【{deployment}】{deploy_res_list}")
                return deploy_res_list
            else:
                nms_not_confirm = result[0][1]
                if nms_not_confirm:
                    content = f'master(admis)返回: 新服务免确认已启用【{env}】【{namespace}】【{deployment}】允许部署/扩缩容,因为k8s_res_control表中找不到该服务,该服务不会被管控，也不会配置固定节点均衡模式（未开启则忽略）。'
                    logger.warning(content)
                    return [200, content]
                else:
                    content = f"master(admis)返回:【{env}】【{namespace}】【{deployment}】部署失败: k8s_res_control表中找不到该服务，且未开启新服务免确认，请先新增服务。"
                    logger.warning(content)
                    return [404, content]
        else:
            return [200, '非管控命名空间，直接放行']
    except ServerException as e:
        content = f"master(admis)返回:【{env}】【{namespace}】【{deployment}】查询数据库失败：{e}"
        logger.error(content)
        return [503, '查询数据库异常']


def send_msg(content):
    response = ""
    if MSG_TYPE == "wecom":
        response = wecom(MSG_TOKEN, content)
    if MSG_TYPE == "dingding":
        response = wecom(MSG_TOKEN, content)
    if MSG_TYPE == "feishu":
        response = wecom(MSG_TOKEN, content)
    return f'【{MSG_TYPE}】{response}'


def wecom(webhook, content, at=""):
    webhook = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=' + webhook
    headers = {'Content-Type': 'application/json'}
    params = {'msgtype': 'markdown', 'markdown': {'content': f"{content}<@{at}>"}}
    data = bytes(json.dumps(params), 'utf-8')
    response = requests.post(webhook, headers=headers, data=data)
    logger.info(f'【wecom】{response.json()}')
    return response.json()


def dingding(webhook, content, at=""):
    webhook = 'https://oapi.dingtalk.com/robot/send?access_token=' + webhook
    headers = {'Content-Type': 'application/json'}
    params = {"msgtype": "markdown", "markdown": {"title": "告警", "text": content}, "at": {"atMobiles": [at]}}
    data = bytes(json.dumps(params), 'utf-8')
    response = requests.post(webhook, headers=headers, data=data)
    logger.info(f'【dingding】{response.json()}')
    return response.json()


def feishu(webhook, content, at=""):
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
    logger.info(f'【feishu】{response.json()}')
    return response.json()


def get_list_from_resources(env_value):
    """获取资源表信息，取最近10天cpu数据最高的一天的数据"""
    query = f"""
        select
            `date`,
            env,
            namespace,
            deployment,
            pod_count,
            p95_pod_cpu_pct,
            p95_pod_wss_pct,
            request_pod_cpu_m,
            request_pod_mem_mb,
            limit_pod_cpu_m,
            limit_pod_mem_mb,
            p95_pod_load,
            p95_pod_wss_mb
        from kubedoor.k8s_resources
        where date = (
            SELECT `date`
            FROM kubedoor.k8s_resources
            WHERE `date` >= toDate(today() - 10) and env = '{env_value}'
            GROUP BY `date`
            order by SUM(pod_count * p95_pod_load) desc
            limit 1
        ) and env = '{env_value}'
    """
    result = ckclient.execute(query)
    ckclient.disconnect()
    logger.info("提取最近10天cpu最高的一天的数据：")
    for i in result:
        logger.info(i)
    return result


def is_init_or_update(env_value):
    """判断管控表是初始化还是更新"""
    query = f"""select * from kubedoor.k8s_res_control where env = '{env_value}'"""
    result = ckclient.execute(query)
    if not result:  # 初始化
        return True
    else:  # 更新
        return False


def parse_insert_data(srv):
    """将从resource表查到的指标数据，解析为可以存入管控表的数据"""
    # 把request-cpu,request-mem,limit-cpu,limit-mem这四个值转化为整数
    srv = list(srv)
    for j in range(7, 11):
        srv[j] = int(srv[j])
    tmp = [
        srv[1],
        srv[2],
        srv[3],
        srv[4],
        srv[4],
        -1,
        srv[5],
        srv[6],
        int(srv[11] * 1000),
        int(srv[12]),
        srv[9],
        srv[10],
        srv[0],
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        datetime(2000, 1, 1, 0, 0, 0),
    ]
    return tmp


def init_control_data(metrics_list_ck):
    '''初始化管控表'''
    metrics_list = list()
    for srv in metrics_list_ck:
        tmp = parse_insert_data(srv)
        logger.info(tmp)
        metrics_list.append(tmp)
    batch_size = 10000
    for i in range(0, len(metrics_list), batch_size):
        begin = time.time()
        batch_data = metrics_list[i : i + batch_size]
        try:
            ckclient.execute("INSERT INTO k8s_res_control VALUES", batch_data, types_check=True)
            logger.info(
                f"== count: insert batch {i//batch_size}",
                "耗时：{:.2f}s".format(time.time() - begin),
            )
        except ServerException as e:
            logger.exception("Failed to insert batch {}: {}", i // batch_size, e)
            return False

    ckclient.disconnect()
    return True


def update_control_data(metrics_list_ck):
    """更新管控表"""
    for i in metrics_list_ck:
        (
            date,
            env,
            namespace,
            deployment,
            pod_count,
            p95_pod_cpu_pct,
            p95_pod_wss_pct,
            request_pod_cpu_m,
            request_pod_mem_mb,
            limit_pod_cpu_m,
            limit_pod_mem_mb,
            p95_pod_load,
            p95_pod_wss_mb,
        ) = i
        date_str = date.strftime('%Y-%m-%d %H:%M:%S')
        sql = f"select 1 from kubedoor.k8s_res_control where env = '{env}' and namespace = '{namespace}' and deployment = '{deployment}'"
        data = ckclient.execute(sql)
        if data:  # 更新
            request_cpu_m = p95_pod_load * 1000
            try:
                update_sql = f"""
                    alter table kubedoor.k8s_res_control
                    update
                        `update` = '{date_str}',
                        pod_count = {pod_count},
                        p95_pod_cpu_pct = {p95_pod_cpu_pct},
                        p95_pod_mem_pct = {p95_pod_wss_pct},
                        request_cpu_m = {int(request_cpu_m)},
                        request_mem_mb = {int(p95_pod_wss_mb)}
                    where
                        env = '{env}' and namespace = '{namespace}' and deployment = '{deployment}'
                """
                update_data = ckclient.execute(update_sql)
            except Exception as e:
                logger.exception("Failed to execute {}: {}", update_sql, e)
                ckclient.disconnect()
                return False
        else:  # 添加
            content = f"采集高峰期数据更新到管控表时，检测到新服务【{env}】【{namespace}】【{deployment}】,将新增到管控表。"
            logger.info(content)
            send_msg(content)
            tmp = ""
            try:
                tmp = parse_insert_data(i)
                ckclient.execute("INSERT INTO k8s_res_control VALUES", [tuple(tmp)], types_check=True)
            except Exception as e:
                logger.exception("Failed to insert {}: {}", [tuple(tmp)], e)
                ckclient.disconnect()
                return False
    ckclient.disconnect()
    return True


def get_deployment_from_control_data(deployment_list, num, type, env):
    """根据指定指标获取排名靠前的deployment"""
    logger.info(f"开始获取 {env} 环境中排名靠前的deployment，类型: {type}，数量限制: {num}")
    top_deployments = []
    
    # 构造排序字段
    order_field = "request_cpu_m" if type == "cpu" else "request_mem_mb"
    
    # 为每个deployment查询资源控制数据
    for index, deployment in enumerate(deployment_list):
        namespace = deployment.get('namespace')
        pod = deployment.get('pod')
        # 从pod名称提取deployment_name，去掉最后两个由-分隔的部分
        deployment_name = pod.rsplit('-', 2)[0] if pod else ""
        logger.info(f"[{index+1}/{len(deployment_list)}] 查询deployment: {namespace}/{deployment_name}，原始Pod名称: {pod}")
        
        # 构建查询语句
        query = f"""
            SELECT deployment, namespace, request_cpu_m, request_mem_mb 
            FROM kubedoor.k8s_res_control 
            WHERE env = '{env}' AND deployment = '{deployment_name}' AND namespace = '{namespace}'
        """
        
        try:
            # 执行查询
            result = ckclient.execute(query)
            if result and len(result) > 0:
                # 结果转为字典
                deployment_data = {
                    'deployment': result[0][0],  # deployment
                    'namespace': result[0][1],   # namespace
                    'request_cpu_m': result[0][2],  # CPU
                    'request_mem_mb': result[0][3]  # 内存
                }
                logger.info(f"查询成功: {namespace}/{deployment_name}, CPU: {deployment_data['request_cpu_m']}m, 内存: {deployment_data['request_mem_mb']}MB")
                top_deployments.append(deployment_data)
            else:
                logger.warning(f"未找到 {namespace}/{deployment_name} 的资源管控数据")
        except Exception as e:
            logger.error(f"查询 deployment {deployment_name} 资源数据失败: {e}")
    
    logger.info(f"查询完成，共找到 {len(top_deployments)} 个deployment的资源管控数据")
    
    # 根据指定字段排序
    if top_deployments:
        top_deployments.sort(key=lambda x: x[order_field], reverse=True)
        # 创建最终部署名称列表
        final_deploy_names = []
        for d in top_deployments:
            final_deploy_names.append(f"{d.get('namespace', 'unknown')}/{d.get('deployment', 'unknown')}")
        logger.info(f"最终返回 {len(top_deployments)} 个deployment: {json.dumps(final_deploy_names)}")
        
        # 限制返回数量
        if num > 0 and len(top_deployments) > num:
            logger.info(f"限制返回前 {num} 个deployment")
            top_deployments = top_deployments[:num]
    
    return top_deployments


async def get_node_cpu_per(env_value):
    query = f'(1 - avg(irate(node_cpu_seconds_total{{mode="idle",{PROM_K8S_TAG_KEY}="{env_value}"}}[2m])) by (instance,nodeAppType,origin_prometheus))*100'
    try:
        logger.info(query)
        response = requests.get(get_prom_url(), params={'query': query})
        logger.info(get_prom_url())
        response.raise_for_status()
        data = response.json().get("data").get("result")
        cpu_list = [{'name': i.get('metric').get('instance'), 'percent': float(i['value'][1])} for i in data if 'value' in i and len(i['value']) > 1]
        logger.info(f'从prometheus查询节点cpu使用率{cpu_list}')
        cpu_list.sort(key=lambda x: x['percent'])
        logger.info(f'节点cpu使用率从小到大排序{cpu_list}')
        return cpu_list
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error getting node cpu usage percent from Prometheus: {e}")
