import asyncio
import json
import sys
import time
import base64
import aiohttp
from datetime import datetime, timedelta
from aiohttp import web, WSMsgType
from loguru import logger
import utils, prom_real_time_data
from multidict import MultiDict

logger.remove()
logger.add(
    sys.stderr,
    format='<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> [<level>{level}</level>] <level>{message}</level>',
    level='INFO',
)


async def get_authorization_header(username, password):
    credentials = f'{username}:{password}'
    encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
    return f'Basic {encoded_credentials}'


async def forward_request(request):
    try:
        data = await request.text()

        permission = request.headers.get('X-User-Permission', '')
        if permission == 'read' and not data.strip().lower().startswith('select'):
            return web.Response(status=403)
        if not data.strip().lower().startswith(('select', 'alter', 'insert')):
            return web.Response(status=403)
        data = data.replace('__KUBEDOORDB__', utils.CK_DATABASE)
        logger.info(f'📐{data}')

        if data.strip().lower().startswith(('alter')):
            utils.ck_alter(data)
            utils.ck_optimize()
            logger.info("SQL: 数据更新")
            return web.json_response({"msg": "SQL: 数据更新完成"})
        else:
            TARGET_URL = f'http://{utils.CK_HOST}:{utils.CK_HTTP_PORT}/?add_http_cors_header=1&default_format=JSONCompact'
            headers = {
                'Authorization': await get_authorization_header(utils.CK_USER, utils.CK_PASSWORD),
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
                'Content-Type': 'text/plain',
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(TARGET_URL, data=data, headers=headers) as response:
                    if response.content_type == 'application/json':
                        response_data = await response.json()
                    else:
                        text = await response.text()
                        response_data = {"msg": text}
                    return web.json_response(response_data)
    except Exception as e:
        logger.error(f"Error in forward_request: {e}")
        return web.json_response({"error": str(e)}, status=500)


clients = {}


async def websocket_handler(request):
    env = request.query.get("env")
    ver = request.query.get("ver", "unknown")
    if not env:
        return web.Response(text="缺少 env 参数", status=400)
    if env in clients and clients[env]["online"]:
        return web.Response(text="目标客户端已在线", status=409)

    ws = web.WebSocketResponse()
    await ws.prepare(request)

    logger.info(f"客户端连接成功，env={env} ver={ver}")
    if env not in clients:
        # 如果是新客户端，初始化状态
        clients[env] = {"ws": ws, "ver": ver, "last_heartbeat": time.time(), "online": True}
        utils.ck_init_agent_status(env)
    else:
        # 如果是重连客户端，更新 WebSocket 和状态
        clients[env]["ws"] = ws
        clients[env]["ver"] = ver
        clients[env]["last_heartbeat"] = time.time()
        clients[env]["online"] = True

    try:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                try:
                    data = json.loads(msg.data)
                except json.JSONDecodeError:
                    logger.error(f"收到无法解析的消息：{msg.data}")
                    continue

                if data.get("type") == "heartbeat":
                    # 更新心跳时间
                    clients[env]["last_heartbeat"] = time.time()
                    clients[env]["online"] = True
                    # logger.info(f"[心跳]客户端 env={env} ver={ver}")
                elif data.get("type") == "admis":
                    request_id = data["request_id"]
                    namespace = data["namespace"]
                    deployment = data["deployment"]
                    logger.info(f"==========客户端 env={env} {request_id} {namespace} {deployment}")
                    deploy_res = utils.get_deploy_admis(env, namespace, deployment)
                    await ws.send_json({"type": "admis", "request_id": request_id, "deploy_res": deploy_res})

                elif data.get("type") == "response":
                    # 收到客户端的响应，存储到客户端的响应队列中
                    request_id = data["request_id"]
                    response = data["response"]
                    if "response_queue" in clients[env]:
                        clients[env]["response_queue"][request_id] = response
                    logger.info(f"[响应]客户端 env={env}: request_id={request_id}：{response}")
                else:
                    logger.info(f"收到客户端消息：{msg.data}")
            elif msg.type == WSMsgType.ERROR:
                logger.error(f"客户端连接出错，env={env}")
    except Exception as e:
        logger.error(f"客户端连接异常断开，env={env}，错误：{e}")
    finally:
        # 标记客户端为离线
        if env in clients:
            clients[env]["online"] = False
            logger.info(f"客户端连接关闭，标记为离线，env={env}")

    return ws


async def http_handler(request):
    path = request.path
    method = request.method
    query_params = dict(request.query)
    env = query_params.get("env", None)
    try:
        body = await request.json()
    except:
        body = False
    if not env:
        return web.Response(text="缺少 env 参数", status=400)

    if env not in clients or not clients[env]["online"]:
        return web.Response(text="目标客户端不在线", status=404)

    # 扩缩容接口要查询节点cpu使用率并传给agent
    logger.info(path)
    if path == "/api/scale" and query_params.get("add_label") == 'true':
        node_cpu_list = await utils.get_node_cpu_per(query_params.get("env"))
        body[0]['node_cpu_list'] = node_cpu_list

    # 固定节点均衡模式，增加节点微调能力
    if path == "/api/balance_node":
        source = body.get('source')
        num = body.get('num')
        type = body.get('type')
        logger.info(body)

        # 查询源节点所有deployment列表
        deployment_list = utils.get_node_deployments(source, env)
        top_deployments = utils.get_deployment_from_control_data(deployment_list, num, type, env)
        body['top_deployments'] = top_deployments

    # 向目标客户端发送消息
    request_id = str(time.time())  # 使用时间戳作为唯一请求 ID
    message = {
        "type": "request",
        "request_id": request_id,
        "method": method,
        "path": path,
        "query": query_params,
        "body": body,
    }
    await clients[env]["ws"].send_json(message)  # 使用 send_json 发送 JSON 数据
    logger.info(f"[请求]客户端 env={env}: {message}")

    # 等待客户端响应
    if "response_queue" not in clients[env]:
        clients[env]["response_queue"] = {}

    try:
        for _ in range(120 * 10):  # 等待 120 秒，检查响应队列
            if request_id in clients[env]["response_queue"]:
                response = clients[env]["response_queue"].pop(request_id)
                return web.json_response(response)
            await asyncio.sleep(0.1)
    except Exception as e:
        logger.error(f"等待客户端响应时发生错误，env={env}, 错误：{e}")

    return web.Response(text="客户端未响应", status=504)


async def status_handler(request):
    agent_info = utils.ck_agent_info()
    agents_status = {
        env: {
            "online": data["online"],
            "last_heartbeat": datetime.fromtimestamp(data["last_heartbeat"]).strftime("%Y-%m-%d %H:%M:%S"),
            "ver": data["ver"],
        }
        for env, data in clients.items()
    }
    agents = utils.merge_dicts(agents_status, agent_info)
    return web.json_response({'data': agents})


async def prom_query_handler(request):
    env_value = request.query.get('env')
    namespace_value = request.query.get('ns')
    metrics_data = prom_real_time_data.get_metrics_data(env_value, namespace_value)
    final_data = prom_real_time_data.process_metrics_data(metrics_data)
    return web.json_response({'data': final_data})


async def prom_ns_handler(request):
    env_value = request.query.get('env')
    if not env_value:
        return web.json_response({'message': 'env query parameter is required'}, status=400)
    try:
        namespaces = utils.fetch_prom_namespaces(env_value)
        return web.json_response({'data': namespaces})
    except Exception as e:
        return web.json_response({'message': str(e)}, status=500)


async def prom_env_handler(request):
    try:
        envs = utils.fetch_prom_envs()
        return web.json_response({'data': envs})
    except Exception as e:
        return web.json_response({'message': str(e)}, status=500)


async def heartbeat_check():
    """定期检查客户端的心跳状态"""
    while True:
        for env, data in clients.items():
            if data["online"] and time.time() - data["last_heartbeat"] > 5:
                # 标记超时客户端为离线
                data["online"] = False
                logger.warning(f"客户端 env={env} 超时，标记为离线")
        await asyncio.sleep(3)


async def cron_peak_data(request):
    param_combinations = utils.ck_agent_collect_info()

    # 使用 streaming response 给客户端逐个返回响应
    async def stream_responses():
        for env, peak_hours in param_combinations:
            query_params = MultiDict([("env", env), ("peak_hours", peak_hours)])
            fake_request = request.clone()
            fake_request._rel_url = fake_request._rel_url.update_query(query_params)
            response = await init_peak_data(fake_request)
            # 解析 JSON 响应并确保中文字符不被转义
            response_json = json.loads(response.body.decode('utf-8'))
            json_str = json.dumps(response_json, ensure_ascii=False)
            # 将 JSON 字符串转换为字节对象再返回
            yield (json_str + '\n').encode('utf-8')

    # 返回流式响应
    return web.Response(
        content_type='application/json',  # 设置正确的 content-type
        charset='utf-8',  # 单独设置字符集
        body=stream_responses(),  # 使用 stream_responses 来逐个返回数据
    )


async def init_peak_data(request):
    """初始化/更新原始资源表k8s_resources，初始化/更新资源管控表k8s_res_control"""
    try:
        env_key = utils.PROM_K8S_TAG_KEY
        env_value = request.query.get("env")
        days = int(request.query.get("days", 2))  # 不传则采集昨天+今天
        peak_hours = request.query.get("peak_hours", "10:00:00-11:30:00")
        logger.info(f"🐛开始获取{env_value}，{days}天，每日【{peak_hours}】高峰期数据")
        namespace_str = ".*"  # utils.NAMESPACE_LIST.replace(",", "|")
        duration_str, start_time_part, end_time_part = utils.calculate_peak_duration_and_end_time(peak_hours)

        for i in range(0, days):
            # 计算结束时间字符串
            current_date = datetime.now().date()
            start_time_full = datetime.combine(current_date, start_time_part) - timedelta(days=i)
            end_time_full = datetime.combine(current_date, end_time_part) - timedelta(days=i)
            if datetime.now() < end_time_full:
                logger.info(f"今天的高峰期还未结束，跳过{current_date}的数据采集")
                continue
            utils.check_and_delete_day_data(end_time_full, env_value)
            logger.info(f"🚀获取{end_time_full}的数据======")
            k8s_metrics_list = utils.merged_dict(env_key, env_value, namespace_str, duration_str, start_time_full, end_time_full)
            utils.metrics_to_ck(k8s_metrics_list)
        logger.info(f"🚀{env_value}: 高峰期数据采集流程结束,开始取最近10天cpu使用最高的一天pod数据, 写入管控表")

        # 采集完成后，取最近10天cpu数据最高的一天pod，数据写入管控表
        resources = utils.get_list_from_resources(env_value)
        if utils.is_init_or_update(env_value):
            # 初始化
            logger.info(f"🌊{env_value}: 初始化管控表======")
            flag = utils.init_control_data(resources)
        else:
            # 更新
            logger.info(f"🌊{env_value}: 更新管控表======")
            flag = utils.update_control_data(resources)

        if not flag:
            return web.json_response({"message": f"{env_value}: 写入管控表执行失败，详情见kubedoor-master日志"}, status=500)
        return web.json_response({"message": f"{env_value}: 执行完成"})
    except Exception as e:
        logger.error(f"Error in table: {e}")
        return web.json_response({"message": str(e)}, status=500)


async def start_background_tasks(app):
    """启动后台任务"""
    app["heartbeat_task"] = asyncio.create_task(heartbeat_check())


async def cleanup_background_tasks(app):
    """清理后台任务"""
    app["heartbeat_task"].cancel()
    await app["heartbeat_task"]


app = web.Application()
app.router.add_get("/ws", websocket_handler)
app.router.add_post('/api/sql', forward_request)
app.router.add_get("/api/agent_status", status_handler)
app.router.add_get("/api/prom_ns", prom_ns_handler)
app.router.add_get("/api/prom_env", prom_env_handler)
app.router.add_get("/api/prom_query", prom_query_handler)
app.router.add_get("/api/init_peak_data", init_peak_data)
app.router.add_get("/api/cron_peak_data", cron_peak_data)
app.router.add_route('*', "/api/{tail:.*}", http_handler)

# 在应用启动和关闭时管理后台任务
app.on_startup.append(start_background_tasks)
app.on_cleanup.append(cleanup_background_tasks)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=80)
