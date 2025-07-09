import requests
import json
import utils


PROM_K8S_TAG_KEY = utils.PROM_K8S_TAG_KEY
PROMETHEUS_URL = f"{utils.PROM_URL}/api/v1/query"


# 定义PromQL查询
def process_promql_queries(env_key, env_value, namespace_value):
    if namespace_value:
        namespace_part = f'namespace="{namespace_value}",'
    else:
        namespace_part = ""

    promql_queries = {
        "pod_count": f'max by({env_key},namespace,deployment)(kube_deployment_spec_replicas{{{namespace_part} {env_key}="{env_value}"}})',
        "avg_cpu_usage": f'avg by({env_key},namespace,deployment) (rate(container_cpu_usage_seconds_total{{{namespace_part} {env_key}="{env_value}",container!="",container!="POD"}}[2m]) * on ({env_key},namespace,pod) group_left(deployment) label_replace(kube_pod_owner{{owner_kind="ReplicaSet", {namespace_part} {env_key}="{env_value}"}},"deployment","$1","owner_name","(.*)-[a-z0-9]+"))*1000',
        "max_cpu_usage": f'max by({env_key},namespace,deployment) (rate(container_cpu_usage_seconds_total{{{namespace_part} {env_key}="{env_value}",container!="",container!="POD"}}[2m]) * on ({env_key},namespace,pod) group_left(deployment) label_replace(kube_pod_owner{{owner_kind="ReplicaSet", {namespace_part} {env_key}="{env_value}"}},"deployment","$1","owner_name","(.*)-[a-z0-9]+"))*1000',
        "cpu_requests": f'avg by({env_key},namespace,deployment) (kube_pod_container_resource_requests{{resource="cpu", {namespace_part} {env_key}="{env_value}"}} * on ({env_key},namespace,pod) group_left(deployment) label_replace(kube_pod_owner{{owner_kind="ReplicaSet", {namespace_part} {env_key}="{env_value}"}},"deployment","$1","owner_name","(.*)-[a-z0-9]+"))*1000',
        "cpu_limit": f'avg by({env_key},namespace,deployment) (kube_pod_container_resource_limits{{resource="cpu", {namespace_part} {env_key}="{env_value}"}} * on ({env_key},namespace,pod) group_left(deployment) label_replace(kube_pod_owner{{owner_kind="ReplicaSet", {namespace_part} {env_key}="{env_value}"}},"deployment","$1","owner_name","(.*)-[a-z0-9]+"))*1000',
        "avg_memory_wss": f'max by({env_key},namespace,deployment) (container_memory_working_set_bytes{{{namespace_part} {env_key}="{env_value}",container!="",container!="POD"}} * on ({env_key},namespace,pod) group_left(deployment) label_replace(kube_pod_owner{{owner_kind="ReplicaSet", {namespace_part} {env_key}="{env_value}"}},"deployment","$1","owner_name","(.*)-[a-z0-9]+"))/1024/1024',
        "max_memory_wss": f'max by({env_key},namespace,deployment) (container_memory_working_set_bytes{{{namespace_part} {env_key}="{env_value}",container!="",container!="POD"}} * on ({env_key},namespace,pod) group_left(deployment) label_replace(kube_pod_owner{{owner_kind="ReplicaSet", {namespace_part} {env_key}="{env_value}"}},"deployment","$1","owner_name","(.*)-[a-z0-9]+"))/1024/1024',
        "mem_requests": f'avg by({env_key},namespace,deployment) (kube_pod_container_resource_requests{{resource="memory", {namespace_part} {env_key}="{env_value}"}} * on ({env_key},namespace,pod) group_left(deployment) label_replace(kube_pod_owner{{owner_kind="ReplicaSet", {namespace_part} {env_key}="{env_value}"}},"deployment","$1","owner_name","(.*)-[a-z0-9]+"))/1024/1024',
        "mem_limit": f'avg by({env_key},namespace,deployment) (kube_pod_container_resource_limits{{resource="memory", {namespace_part} {env_key}="{env_value}"}} * on ({env_key},namespace,pod) group_left(deployment) label_replace(kube_pod_owner{{owner_kind="ReplicaSet", {namespace_part} {env_key}="{env_value}"}},"deployment","$1","owner_name","(.*)-[a-z0-9]+"))/1024/1024',
    }
    return promql_queries


# Prometheus查询函数
def query_prometheus(promql):
    params = {'query': promql}
    try:
        response = requests.get(PROMETHEUS_URL, params=params)
        response.raise_for_status()
        data = response.json()
        return data['data']['result']
    except requests.exceptions.RequestException as e:
        print(f"Error querying Prometheus: {e}")
        return []


# 获取所有指标的数据
def get_metrics_data(env_value, namespace_value):
    # 用于存储所有数据的字典
    metrics_data = {}
    query_dict = process_promql_queries(PROM_K8S_TAG_KEY, env_value, namespace_value)
    # 执行每个查询
    for metric, query in query_dict.items():
        result = query_prometheus(query)
        metrics_data[metric] = result

    return metrics_data


# 四舍五入到整数
def round_to_int(value):
    try:
        return round(float(value))
    except ValueError:
        return 0


# 处理并整合指标数据
def process_metrics_data(metrics_data):
    # 最终的结果列表
    final_data = []

    # 提取所有的env, namespace, deployment组合
    deployments = set()
    for metric in metrics_data['pod_count']:
        env = metric['metric'][PROM_K8S_TAG_KEY]
        namespace = metric['metric']['namespace']
        deployment = metric['metric']['deployment']
        deployments.add((env, namespace, deployment))

    # 遍历每个deployment，匹配所有指标
    for env, namespace, deployment in deployments:
        # 创建每个deployment的结果列表
        row = [
            env,
            namespace,
            deployment,
            0,  # pod_count
            0,  # avg_cpu_usage
            0,  # max_cpu_usage
            0,  # cpu_requests
            0,  # cpu_limit
            0,  # avg_memory_wss
            0,  # max_memory_wss
            0,  # mem_requests
            0,  # mem_limit
        ]

        # 获取Pod数
        for metric in metrics_data['pod_count']:
            if (
                metric['metric'][PROM_K8S_TAG_KEY] == env
                and metric['metric']['namespace'] == namespace
                and metric['metric']['deployment'] == deployment
            ):
                row[3] = round_to_int(metric['value'][1])

        # 获取其他指标
        for metric_idx, metric in enumerate(
            [
                'avg_cpu_usage',
                'max_cpu_usage',
                'cpu_requests',
                'cpu_limit',
                'avg_memory_wss',
                'max_memory_wss',
                'mem_requests',
                'mem_limit',
            ],
            start=4,
        ):
            for data in metrics_data[metric]:
                if (
                    data['metric'][PROM_K8S_TAG_KEY] == env
                    and data['metric']['namespace'] == namespace
                    and data['metric']['deployment'] == deployment
                ):
                    row[metric_idx] = round_to_int(data['value'][1])

        final_data.append(row)

    return final_data
