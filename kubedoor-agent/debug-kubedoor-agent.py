import asyncio
import json
import sys
from aiohttp import web
from kubernetes_asyncio import client, config
from kubernetes_asyncio.client.rest import ApiException
from loguru import logger

# 配置日志
logger.remove()
logger.add(
    sys.stderr,
    format='<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> [<level>{level}</level>] <level>{message}</level>',
    level='INFO',
)


# 全局变量
v1 = None  # AppsV1Api
batch_v1 = None  # BatchV1Api
core_v1 = None  # CoreV1Api
custom_api = None  # CustomObjectsApi（用于访问Metrics API）


async def init_kubernetes():
    """在程序启动时加载 Kubernetes 配置并初始化客户端"""
    global v1, batch_v1, core_v1, custom_api
    try:
        # 使用本地kubeconfig文件而不是集群内配置
        logger.info("开始加载Kubernetes配置文件...")
        config_path = "D:\\K8S-config\\kubeconfig.json"
        logger.info(f"配置文件路径: {config_path}")

        # 注意：load_kube_config是异步函数，需要await
        await config.load_kube_config(config_file=config_path)
        configuration = client.Configuration.get_default_copy()
        configuration.verify_ssl = False
        client.Configuration.set_default(configuration)
        v1 = client.AppsV1Api()
        batch_v1 = client.BatchV1Api()
        core_v1 = client.CoreV1Api()
        custom_api = client.CustomObjectsApi()
        logger.info("Kubernetes API客户端初始化成功")

        # 测试连接是否成功
        logger.info("正在测试Kubernetes连接...")
        return True
    except Exception as e:
        logger.error(f"加载 Kubernetes 配置失败: {e}")
        logger.error(f"错误类型: {type(e).__name__}")
        logger.error(f"错误详情: {str(e)}")
        raise


async def get_namespace_events(request):
    """获取指定命名空间的事件，如果不指定namespace则获取所有命名空间的事件"""
    namespace = request.query.get("namespace")

    try:
        # 构造查询条件
        field_selector = None
        if namespace:
            field_selector = f"involvedObject.namespace={namespace}"
            logger.info(f"获取命名空间 {namespace} 的事件")
        else:
            logger.info("获取所有命名空间的事件")

        # 获取事件
        events = await core_v1.list_event_for_all_namespaces(field_selector=field_selector, _request_timeout=30)

        # 格式化事件数据
        event_list = []
        for event in events.items:
            event_list.append(
                {
                    "name": event.metadata.name,
                    "namespace": event.metadata.namespace,
                    "type": event.type,
                    "reason": event.reason,
                    "message": event.message,
                    "involved_object": {
                        "kind": event.involved_object.kind,
                        "name": event.involved_object.name,
                        "namespace": event.involved_object.namespace,
                    },
                    "count": event.count,
                    "first_timestamp": event.first_timestamp.isoformat() if event.first_timestamp else None,
                    "last_timestamp": event.last_timestamp.isoformat() if event.last_timestamp else None,
                    "source": {"component": event.source.component, "host": event.source.host} if event.source else None,
                }
            )

        logger.info(f"获取事件成功，共 {len(event_list)} 条")
        return web.json_response({"events": event_list, "success": True})
    except ApiException as e:
        error_message = f"获取事件失败: {e}"
        logger.error(error_message)
        return web.json_response({"message": error_message, "success": False}, status=500)
    except Exception as e:
        error_message = f"获取事件时发生未知错误: {e}"
        logger.exception(error_message)
        return web.json_response({"message": error_message, "success": False}, status=500)


async def setup_routes(app):
    app.router.add_get('/api/events', get_namespace_events)


async def start_http_server():
    """启动 HTTP 服务器"""
    app = web.Application()
    await setup_routes(app)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    logger.info("HTTP 服务器已启动，监听端口 8080")
    while True:
        await asyncio.sleep(3600)


async def test_kubernetes_connection():
    """测试Kubernetes连接是否成功"""
    try:
        # 尝试获取所有命名空间列表来测试连接
        logger.info("正在获取命名空间列表以测试连接...")
        namespaces = await core_v1.list_namespace()
        logger.info(f"成功连接到Kubernetes集群! 获取到 {len(namespaces.items)} 个命名空间")
        # 打印前5个命名空间名称作为示例
        ns_names = [ns.metadata.name for ns in namespaces.items[:5]]
        logger.info(f"命名空间示例: {', '.join(ns_names)}")
        return True
    except ApiException as e:
        logger.error(f"连接Kubernetes API失败: {e}")
        logger.error(f"状态码: {e.status}, 原因: {e.reason}")
        return False
    except Exception as e:
        logger.error(f"测试Kubernetes连接时发生未知错误: {e}")
        logger.error(f"错误类型: {type(e).__name__}")
        return False


async def main():
    """主函数"""
    # 初始化 Kubernetes 配置
    await init_kubernetes()

    # 测试Kubernetes连接
    connection_success = await test_kubernetes_connection()
    if connection_success:
        logger.info("✅ Kubernetes连接测试成功，继续启动HTTP服务器")
    else:
        logger.error("❌ Kubernetes连接测试失败，但仍将尝试启动HTTP服务器")

    # 启动HTTP服务器
    await start_http_server()


if __name__ == "__main__":
    import sys

    # 检查是否有测试参数
    if len(sys.argv) > 1 and sys.argv[1] == "--test-connection":
        # 只测试Kubernetes连接
        async def test_only():
            try:
                # 正确地等待异步初始化函数
                await init_kubernetes()
                connection_success = await test_kubernetes_connection()
                if connection_success:
                    logger.info("✅ Kubernetes连接测试成功!")
                    return 0
                else:
                    logger.error("❌ Kubernetes连接测试失败!")
                    return 1
            except Exception as e:
                logger.error(f"测试过程中发生错误: {e}")
                logger.error(f"错误类型: {type(e).__name__}")
                logger.error(f"错误详情: {str(e)}")
                return 1
            finally:
                # 确保关闭所有客户端会话
                try:
                    await client.api_client.rest_client.pool_manager.close()
                    logger.info("已关闭所有客户端会话")
                except Exception as e:
                    logger.error(f"关闭客户端会话时出错: {e}")

        sys.exit(asyncio.run(test_only()))
    else:
        # 正常启动完整应用
        asyncio.run(main())
