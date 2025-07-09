import httpx
import json
import logging
from typing import Union
from mcp.server.fastmcp import FastMCP

# 配置日志格式
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

mcp = FastMCP("KubeDoor-MCP")
MASTER = "http://kubedoor-master.kubedoor"


async def make_request(url: str, params: Union[dict, list], method: str = 'GET') -> str:
    async with httpx.AsyncClient() as client:
        try:
            if method.upper() == 'GET':
                response = await client.get(url, params=params, timeout=30.0)
            elif method.upper() == 'POST':
                response = await client.post(url, json=params, timeout=30.0)
            else:
                return f"不支持的请求方法: {method}"

            response.raise_for_status()
            response_text = response.text
            try:
                json_data = json.loads(response_text)
                return json_data.get('message', response_text)
            except json.JSONDecodeError:
                return response_text
        except Exception as e:
            logger.error(f"请求失败: {str(e)}")
            return "数据获取失败"


@mcp.tool(description="进入Pod获取JAVA进程的内存dump文件")
async def get_pod_jvm_dump(namespace: str, pod: str, k8s: str) -> str:
    """
    Args:
        namespace: Pod所在的命名空间
        pod: Pod的名称
        k8s: K8S集群名称

    Returns:
        str: JAVA进程的内存dump文件下载地址或错误信息
    """
    url = f"{MASTER}/api/pod/auto_dump"
    params = {"env": k8s, "ns": namespace, "pod_name": pod}
    return await make_request(url, params)


@mcp.tool(description="进入Pod获取JAVA进程的JVM内存使用情况")
async def get_pod_jvm_mem(namespace: str, pod: str, k8s: str) -> str:
    """
    Args:
        namespace: Pod所在的命名空间
        pod: Pod的名称
        k8s: K8S集群名称

    Returns:
        str: JVM内存使用情况或错误信息
    """
    url = f"{MASTER}/api/pod/auto_jvm_mem"
    params = {"env": k8s, "ns": namespace, "pod_name": pod}
    return await make_request(url, params)


@mcp.tool(description="进入Pod获取JAVA线程的jstack堆栈跟踪信息")
async def get_pod_jvm_jstack(namespace: str, pod: str, k8s: str) -> str:
    """
    Args:
        namespace: Pod所在的命名空间
        pod: Pod的名称
        k8s: K8S集群名称

    Returns:
        str: JAVA线程的堆栈跟踪信息下载地址或错误信息
    """
    url = f"{MASTER}/api/pod/auto_jstack"
    params = {"env": k8s, "ns": namespace, "pod_name": pod}
    return await make_request(url, params)


@mcp.tool(description="进入Pod获取JAVA进程性能监控及问题诊断的JFR飞行记录文件")
async def get_pod_jvm_jfr(namespace: str, pod: str, k8s: str) -> str:
    """
    Args:
        namespace: Pod所在的命名空间
        pod: Pod的名称
        k8s: K8S集群名称

    Returns:
        str: JFR飞行记录的文件下载地址或错误信息
    """
    url = f"{MASTER}/api/pod/auto_jfr"
    params = {"env": k8s, "ns": namespace, "pod_name": pod}
    return await make_request(url, params)


@mcp.tool(description="删除一个指定的pod")
async def delete_pod(namespace: str, pod: str, k8s: str) -> str:
    """
    Args:
        namespace: Pod所在的命名空间
        pod: Pod的名称
        k8s: K8S集群名称

    Returns:
        str: 删除pod是否成功的信息或错误信息
    """
    url = f"{MASTER}/api/pod/delete_pod"
    params = {"env": k8s, "ns": namespace, "pod_name": pod}
    return await make_request(url, params)


@mcp.tool(description="隔离一个指定的pod(修改Pod的标签,使其脱离Service,Pod状态不变,只是不会再被路由)")
async def modify_pod(namespace: str, pod: str, k8s: str) -> str:
    """
    Args:
        namespace: Pod所在的命名空间
        pod: Pod的名称
        k8s: K8S集群名称

    Returns:
        str: 隔离pod是否成功的信息或错误信息
    """
    url = f"{MASTER}/api/pod/modify_pod"
    params = {"env": k8s, "ns": namespace, "pod_name": pod}
    return await make_request(url, params)


@mcp.tool(description="重启一个指定的deployment")
async def restart_deployment(namespace: str, deployment: str, k8s: str) -> str:
    """
    Args:
        namespace: deployment所在的命名空间
        deployment: deployment的名称
        k8s: K8S集群名称

    Returns:
        str: 重启deployment是否成功的信息或错误信息
    """
    url = f"{MASTER}/api/restart?env={k8s}"
    body = [{"namespace": namespace, "deployment_name": deployment}]
    return await make_request(url, body, "POST")


@mcp.tool(description="扩容/缩容一个指定的deployment的副本数")
async def scale_deployment(namespace: str, deployment: str, replicas: int, k8s: str) -> str:
    """
    Args:
        namespace: deployment所在的命名空间
        deployment: deployment的名称
        replicas: 副本数量/Pod总数
        k8s: K8S集群名称

    Returns:
        str: 扩缩容deployment是否成功的信息或错误信息
    """
    url = f"{MASTER}/api/scale?env={k8s}"
    body = [{"namespace": namespace, "deployment_name": deployment, "num": replicas}]
    return await make_request(url, body, "POST")


@mcp.tool(description="更新一个指定的deployment的镜像标签/版本")
async def update_deployment(namespace: str, deployment: str, image_tag: str, k8s: str) -> str:
    """
    Args:
        namespace: deployment所在的命名空间
        deployment: deployment的名称
        image_tag: 镜像标签/版本
        k8s: K8S集群名称

    Returns:
        str: 更新deployment是否成功的信息或错误信息
    """
    url = f"{MASTER}/api/update-image?env={k8s}"
    params = {"namespace": namespace, "deployment": deployment, "image_tag": image_tag}
    return await make_request(url, params)


@mcp.tool(description="查询指定K8S集群的命名空间列表")
async def get_namespaces_list(k8s: str) -> str:
    """
    Args:
        k8s: K8S集群名称

    Returns:
        str: 相应K8S集群的命名空间列表信息或错误信息
    """
    url = f"{MASTER}/api/prom_ns"
    params = {"env": k8s}
    return await make_request(url, params)


@mcp.tool(
    description="查询指定命名空间内的所有deployment(微服务)的资源信息, 返回的每个列表字段,按顺序含义分别是: k8s,namespace,deployment,pod_count,avg_cpu_usage/pod,max_cpu_usage/pod,cpu_requests/pod,cpu_limit/pod,avg_memory_wss/pod,max_memory_wss/pod,mem_requests/pod,mem_limit/pod"
)
async def get_deployments_info(namespace: str, k8s: str) -> str:
    """
    Args:
        namespace: deployment所在的命名空间
        k8s: K8S集群名称

    Returns:
        str: 相应命名空间的deployment列表信息或错误信息
    """
    url = f"{MASTER}/api/prom_query"
    params = {"env": k8s, "ns": namespace}
    return await make_request(url, params)


@mcp.tool(description="获取可操作的K8S集群列表(返回online: true的即为可操作的集群),如果已经提供了K8S集群名称,则不需要调用该工具。")
async def get_k8s_list() -> str:
    """
    Returns:
        str: 返回可操作的K8S集群列表或错误信息
    """
    url = f"{MASTER}/api/agent_status"
    params = {}
    return await make_request(url, params)


@mcp.tool(description="获取指定K8S集群的节点列表及节点资源明细")
async def get_k8s_nodes(k8s: str) -> str:
    """
    Args:
        k8s: K8S集群名称

    Returns:
        str: K8S节点的明细或错误信息
    """
    url = f"{MASTER}/api/nodes"
    params = {"env": k8s}
    return await make_request(url, params)


@mcp.tool(description="获取指定命名空间的K8S事件信息/K8S的运行状况/K8S的异常信息，如果不指定命名空间则默认获取所有命名空间的")
async def get_k8s_events(k8s: str, namespace: str = '') -> str:
    """
    Args:
        namespace: 指定命名空间
        k8s: K8S集群名称

    Returns:
        str: K8S事件信息或错误信息
    """
    url = f"{MASTER}/api/events"
    params = {"env": k8s, "namespace": namespace}
    return await make_request(url, params)


@mcp.tool(description="获取指定deployment(微服务)的Pod列表与Pod资源明细")
async def get_pods(namespace: str, deployment: str, k8s: str) -> str:
    """
    Args:
        namespace: deployment所在的命名空间
        deployment: deployment的名称
        k8s: K8S集群名称

    Returns:
        str: 指定deployment的pod信息或错误信息
    """
    url = f"{MASTER}/api/get_dpm_pods"
    params = {"env": k8s, "namespace": namespace, "deployment": deployment}
    return await make_request(url, params)


@mcp.tool(description="获取指定Pod最新的日志,默认最新的100行,可指定获取行数")
async def get_pods_logs(namespace: str, pod: str, k8s: str, lines: int = 100) -> str:
    """
    Args:
        namespace: pod所在的命名空间
        pod: pod的名称
        lines: 获取最新日志的行数
        k8s: K8S集群名称

    Returns:
        str: pod的日志信息或错误信息
    """
    url = f"{MASTER}/api/pod/get_logs"
    params = {"env": k8s, "ns": namespace, "pod": pod, "lines": lines}
    return await make_request(url, params)


if __name__ == "__main__":
    mcp.run(transport="sse")
