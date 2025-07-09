#!/usr/bin/python3
# coding=utf-8
import os
import sys
import json
import requests
import uvicorn
import asyncio
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from kubernetes import client
from kubernetes.client import Configuration
from kubernetes.client.rest import ApiException
from kubernetes.stream import stream
from loguru import logger
import utils
import uuid

logger.remove()
logger.add(
    sys.stderr,
    format='<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> [<level>{level}</level>] <level>{message}</level>',
    level='INFO',
)
TASK_RESULTS = {}
app = FastAPI()


def load_incluster_config():
    with open('/var/run/secrets/kubernetes.io/serviceaccount/token', 'r') as token_file:
        token = token_file.read()
    configuration = Configuration()
    configuration.host = "https://kubernetes.default.svc"
    configuration.verify_ssl = True
    configuration.ssl_ca_cert = '/var/run/secrets/kubernetes.io/serviceaccount/ca.crt'
    configuration.api_key = {"authorization": f"Bearer {token}"}

    return configuration


def get_pod_isolate_label(pod_name: str):
    return 'app'


async def jfr_upload(env, ns, v1, pod_name, file_name, task_id):
    try:
        logger.info("【JFR-TASK】Waiting for file to be generated...")
        TASK_RESULTS[task_id] = {"status": "waiting sleeping"}
        total_wait_time = 310
        interval = 10
        for i in range(0, total_wait_time, interval):
            progress = min(100, int((i / total_wait_time) * 100))
            TASK_RESULTS[task_id] = {"status": f"waiting sleeping - {progress}% complete"}
            await asyncio.sleep(interval)
            if i + interval >= total_wait_time:
                break
        TASK_RESULTS[task_id] = {"status": "uploading"}
        dlurl = f'{utils.OSS_URL}/{env}/jfr/{file_name}'
        command = f'curl -s -T /{file_name} {dlurl}'
        status, message = await execute_command(command, v1, pod_name, ns)
        if status:
            message = f"jfr文件上传成功，下载地址：\n{dlurl}"
            TASK_RESULTS[task_id] = {"status": "completed", "message": message}
            await execute_command(f"rm -rf /{file_name}", v1, pod_name, ns)
        else:
            message = message + '\n' + f"jfr成功, 文件上传失败"
            TASK_RESULTS[task_id] = {"status": "failed", "message": message}
        send_md(message, env, ns, pod_name)
    except Exception as e:
        logger.exception(f"Task failed: {e}")
        TASK_RESULTS[task_id] = {"status": "failed", "error": str(e)}


async def modify_pod_label(ns: str, pod_name: str):
    try:
        logger.info(f"===开始修改标签 {ns} {pod_name}")
        config = load_incluster_config()
        client.Configuration.set_default(config)
        v1 = client.CoreV1Api()

        # Get the current pod
        pod_data = v1.read_namespaced_pod(name=pod_name, namespace=ns, _request_timeout=30)
        current_labels = pod_data.metadata.labels or {}

        # Modify the label
        isolate_label = get_pod_isolate_label(pod_name)
        labels_app = current_labels.get(isolate_label, False)
        if not labels_app:
            return False, '===app_label_not_found'
        new_label_value = labels_app + '-ALERT'
        current_labels[isolate_label] = new_label_value

        # Update the pod with the new label
        pod_data.metadata.labels = current_labels
        v1.patch_namespaced_pod(name=pod_name, namespace=ns, body=pod_data, _request_timeout=30)
        return True, ''
    except ApiException as e:
        logger.exception(f"Exception when modifying pod label: {e}")
        return False, '===modify_label_failed'


async def delete_pod_fun(ns: str, pod_name: str):
    # await asyncio.sleep(300)
    try:
        config = load_incluster_config()
        client.Configuration.set_default(config)
        v1 = client.CoreV1Api()
        v1.delete_namespaced_pod(name=pod_name, namespace=ns, _request_timeout=30)
        logger.info(f"Pod {pod_name} deleted successfully")
        return True
    except ApiException as e:
        logger.exception(f"Exception when deleting pod: {e}")
        return False


@app.get("/api/pod/modify_pod")
async def modify_pod(env: str, ns: str, pod_name: str):
    # Modify the pod label
    success, status = await modify_pod_label(ns, pod_name)
    if not success:
        return JSONResponse(status_code=500, content={"message": status})
        # raise HTTPException(status_code=500, detail=status)
    # await asyncio.sleep(300)  # Wait for 5 minutes
    # Schedule the pod deletion after 5 minutes without blocking the request
    # asyncio.create_task(delete_pod(ns, pod_name))
    send_md("app label modified successfully", env, ns, pod_name)
    return {"message": f"【{ns}】【{pod_name}】app label modified successfully", "success": True}


@app.get("/api/pod/delete_pod")
async def delete_pod(env: str, ns: str, pod_name: str):
    # Delete the pod label
    success = await delete_pod_fun(ns, pod_name)
    if not success:
        return JSONResponse(status_code=500, content={"message": "Failed to delete pod"})
    send_md("pod deleted successfully", env, ns, pod_name)
    return {"message": f"【{ns}】【{pod_name}】pod deleted successfully", "success": True}


async def get_pod_info(ns, pod_name, v1, type, tail):
    # 返回pod信息
    try:
        v1.read_namespaced_pod(name=pod_name, namespace=ns, _request_timeout=30)
        now = datetime.now()
        formatted_time = now.strftime("%Y%m%d%H%M")
        file_name = f"{type}-{pod_name}-{formatted_time}.{tail}"
        logger.info(f"文件名{file_name}")
        return file_name, None
    except Exception as e:
        logger.error(f"pod [{pod_name}] in namespace [{ns}] not found")
        logger.exception(str(e))
        return "error", f"pod [{pod_name}] in namespace [{ns}] not found"


async def execute_command(command, v1, pod_name, ns):
    logger.info(f"执行命令：{command}")
    exec_command = ['/bin/sh', '-c', f"{command}; echo $?"]
    try:
        resp = stream(
            v1.connect_get_namespaced_pod_exec,
            pod_name,
            ns,
            command=exec_command,
            stderr=True,
            stdin=False,
            stdout=True,
            tty=False,
        )
        # 分割输出，最后一行是状态码
        lines = resp.strip().split('\n')
        status_code = lines[-1]
        output = '\n'.join(lines[:-1])
        if status_code != '0':
            message = f"命令 {command} 执行失败，状态码: {status_code}，输出信息: {output}"
            logger.error(message)
            return False, message
        return True, output
    except client.exceptions.ApiException as e:
        logger.exception(str(e))
        return False, str(e)


async def execute_in_pod(env, ns, v1, pod_name, type, file_name="not_found"):
    status, message = await execute_command(
        "curl -V || (sed -i 's/dl-cdn.alpinelinux.org/repo.huaweicloud.com/g' /etc/apk/repositories && apk add -q curl)",
        v1,
        pod_name,
        ns,
    )
    if not status:
        return status, message
    if type == "dump":
        command = f"env -u JAVA_TOOL_OPTIONS jmap -dump:format=b,file=/{file_name} `pidof -s java`"
        status, message = await execute_command(command, v1, pod_name, ns)
        if status:
            dlurl = f'{utils.OSS_URL}/{env}/dump/{file_name}'
            command = f'curl -s -T /{file_name} {dlurl}'
            status2, message = await execute_command(command, v1, pod_name, ns)
            if status2:
                message = f"dump文件上传成功，下载地址：\n{dlurl}"
                await execute_command(f"rm -rf /{file_name}", v1, pod_name, ns)
            else:
                message = f"dump成功, 文件上传失败"
        else:
            message = f"dump失败"
    if type == "jfr":
        # 解锁JFR功能
        command_unlock = f"env -u JAVA_TOOL_OPTIONS jcmd `pidof -s java` VM.unlock\_commercial\_features"
        status, message = await execute_command(command_unlock, v1, pod_name, ns)
        if not status:
            return status, message + '\n' + "jfr解锁失败"
        command = f"env -u JAVA_TOOL_OPTIONS jcmd `pidof -s java` JFR.start duration=5m filename=/{file_name}"
        status, message = await execute_command(command, v1, pod_name, ns)
        if not status:
            return status, message + '\n' + "开启jfr飞行记录失败"
    if type == "jstack":
        command = f"env -u JAVA_TOOL_OPTIONS jstack -l `pidof -s java` |tee /{file_name}"
        status, jstack_msg = await execute_command(command, v1, pod_name, ns)
        if status:
            dlurl = f'{utils.OSS_URL}/{env}/jstack/{file_name}'
            command = f'curl -s -T /{file_name} {dlurl}'
            status2, message = await execute_command(command, v1, pod_name, ns)
            if status2:
                dlmsg = f"jstack文件上传成功，下载地址：\n{dlurl}"
                await execute_command(f"rm -rf /{file_name}", v1, pod_name, ns)
            else:
                dlmsg = "jstack成功, 文件上传失败"
            message = jstack_msg + '\n' + dlmsg
            send_md(dlmsg, env, ns, pod_name)
        else:
            message = f"jstack失败"
    if type == "jvm_mem":
        # 查询jvm内存
        command = "env -u JAVA_TOOL_OPTIONS jmap -heap `pidof -s java`"
        # command = "ls arthas-boot.jar || curl -s -O https://arthas.aliyun.com/arthas-boot.jar && env -u JAVA_TOOL_OPTIONS java -jar arthas-boot.jar 1 -c 'memory;stop'|sed -n '/memory | plaintext/,/stop | plaintext/{/memory | plaintext/b;/stop | plaintext/b;p}'"
        status, message = await execute_command(command, v1, pod_name, ns)
    return status, message


def send_md(msg, env, ns, pod_name):
    text = f"# 【<font color=\"#5bcc85\">{env}</font>】{ns}\n## {pod_name}\n"
    text += f"{msg}\n"
    utils.send_msg(text)


@app.get("/api/pod/auto_dump")
async def auto_dump(env: str, ns: str, pod_name: str):
    config = load_incluster_config()
    client.Configuration.set_default(config)
    v1 = client.CoreV1Api()
    file_name, err_msg = await get_pod_info(ns, pod_name, v1, "dump", "hprof")
    if file_name == "error":
        return JSONResponse(status_code=500, content={"message": err_msg})
    # 生成 Java 进程对象统计信息直方图
    status, message = await execute_command("env -u JAVA_TOOL_OPTIONS jmap -histo `pidof -s java` |head -n 30", v1, pod_name, ns)
    if status:
        all_msg = "Java 进程对象统计信息直方图:" + '\n' + message
    else:
        all_msg = message + '\n' + "生成 Java 进程对象统计信息直方图失败"
    status, message = await execute_in_pod(env, ns, v1, pod_name, "dump", file_name)
    all_msg = all_msg + '\n' + message
    if status:
        dlurl = f'{utils.OSS_URL}/{env}/dump/{file_name}'
        send_md(all_msg, env, ns, pod_name)
        return {"message": all_msg, "success": True, "link": dlurl}
    return JSONResponse(status_code=500, content={"message": all_msg})


@app.get("/api/pod/auto_jstack")
async def auto_jstack(env: str, ns: str, pod_name: str):
    config = load_incluster_config()
    client.Configuration.set_default(config)
    v1 = client.CoreV1Api()
    file_name, err_msg = await get_pod_info(ns, pod_name, v1, "jstack", "jstack")
    if file_name == "error":
        return JSONResponse(status_code=500, content={"message": err_msg})
    status, message = await execute_in_pod(env, ns, v1, pod_name, "jstack", file_name)
    if status:
        return {"message": message, "success": True}
    else:
        return JSONResponse(status_code=500, content={"message": message})


@app.get("/api/pod/auto_jfr")
async def auto_jfr(env: str, ns: str, pod_name: str, background_tasks: BackgroundTasks):
    config = load_incluster_config()
    client.Configuration.set_default(config)
    v1 = client.CoreV1Api()
    file_name, err_msg = await get_pod_info(ns, pod_name, v1, "jfr", "jfr")
    if file_name == "error":
        return JSONResponse(status_code=500, content={"message": err_msg})
    status, message = await execute_in_pod(env, ns, v1, pod_name, "jfr", file_name)
    if status:
        task_id = str(uuid.uuid4())
        TASK_RESULTS[task_id] = {"status": "processing"}
        background_tasks.add_task(jfr_upload, env, ns, v1, pod_name, file_name, task_id)
        now = datetime.now()
        finish_time = now + timedelta(minutes=6)
        formatted_now = now.strftime("%H:%M:%S")
        formatted_finish = finish_time.strftime("%H:%M:%S")
        link = f'{utils.OSS_URL}/{env}/jfr/{file_name}'
        message = f"飞行记录后台执行需要5分钟，任务ID：{task_id}\n（/api/pod/task_status/{task_id}?env={env}）\n请于{formatted_finish}后，访问以下链接下载:\n{link}"
        send_md(message, env, ns, pod_name)
        return {"message": message, "success": True, 'link': link}
    return JSONResponse(status_code=500, content={"message": message})


@app.get("/api/pod/auto_jvm_mem")
async def auto_jvm_mem(env: str, ns: str, pod_name: str):
    config = load_incluster_config()
    client.Configuration.set_default(config)
    v1 = client.CoreV1Api()
    status, message = await execute_in_pod(env, ns, v1, pod_name, "jvm_mem")
    if status:
        send_md(message, env, ns, pod_name)
        return {"message": message, "success": True}
    return JSONResponse(status_code=500, content={"message": message})


@app.get("/api/pod/task_status/{task_id}")
async def get_task_status(task_id: str):
    if task_id in TASK_RESULTS:
        return TASK_RESULTS[task_id]
    else:
        return {"status": "not found"}


@app.get("/api/pod/get_logs")
async def get_pod_logs(env: str, ns: str, pod: str, lines: int = 100):
    try:
        config = load_incluster_config()
        client.Configuration.set_default(config)
        v1 = client.CoreV1Api()

        # 检查pod是否存在
        try:
            v1.read_namespaced_pod(name=pod, namespace=ns, _request_timeout=30)
        except Exception as e:
            error_msg = f"pod [{pod}] in namespace [{ns}] not found"
            logger.error(error_msg)
            return JSONResponse(status_code=500, content={"message": error_msg})

        # 获取pod日志
        logs = v1.read_namespaced_pod_log(name=pod, namespace=ns, tail_lines=lines, _request_timeout=30)
        return {"message": logs, "success": True}
    except ApiException as e:
        logger.exception(f"获取Pod日志时出现异常: {e}")
        return JSONResponse(status_code=500, content={"message": f"获取Pod日志失败: {str(e)}"})


if __name__ == "__main__":
    uvicorn.run("pod-mgr:app", host="0.0.0.0", workers=1, port=81)
