const dayjs = require("dayjs");
const rssParser = require('rss-parser');
const turndown = require('turndown');
const Api2d = require('api2d');
const { HttpsProxyAgent } = require('https-proxy-agent');
const fetch = require('cross-fetch');
const FormData = require('form-data');
const fs = require('fs');
const path = require('path');

async function processTask(task, isTest = false) {
    try {
        let do_task = false;

        if (isTest) {
            do_task = true;
        } else {
            if (!task.last_time) do_task = true;
            if (task.last_time && dayjs(task.last_time).add(task.minutes, 'minutes').isBefore(dayjs())) {
                do_task = true;
            }
        }

        if (!do_task) return;

        let requestOptions = {};
        const httpProxy = process.env.HTTP_PROXY || process.env.http_proxy;
        const httpsProxy = process.env.HTTPS_PROXY || process.env.https_proxy;

        if (httpProxy) {
            requestOptions.agent = new HttpsProxyAgent(httpProxy);
        } else {
            if (httpsProxy) requestOptions.agent = new HttpsProxyAgent(httpsProxy);
        }

        const parser = new rssParser({ timeout: 10000, requestOptions });
        const feed = await parser.parseURL(task.feed);
        const last = feed.items[0];
        const last_content = last.guid || last.link;
        const old_content = task.last_content;

        if (!isTest) {
            task.last_time = dayjs().format("YYYY-MM-DD HH:mm:ss");
            task.last_content = last_content;
        }

        if (isTest || (old_content && old_content != last_content)) {
            console.log("Processing task", task.title);

            const last_title = last.title?.toLowerCase();

            if (task['keyword']) {
                const keywords = task['keyword'].toLowerCase().split("|");
                let found = false;
                for (const keyword of keywords) {
                    if (last_title.indexOf(keyword) >= 0) found = true;
                }
                if (!found) {
                    console.log(`白名单跳过，${task['keyword']}`);
                    return;
                }
            }

            if (task['bad_keyword']) {
                const bad_keywords = task['bad_keyword'].toLowerCase().split("|");
                let found = false;
                for (const bad_keyword of bad_keywords) {
                    if (last_title.indexOf(bad_keyword) >= 0) found = true;
                }
                if (found) {
                    console.log(`黑名单跳过，${task['bad_keyword']}`);
                    return;
                }
            }

            const keys = task.keys.split("\n").map(item => item.trim());
            const unique_keys = [...new Set(keys)];

            const sendResults = [];

            for (const skey of unique_keys) {
                const c = new turndown();
                const title = `${task.title} 更新了`;
                const short = `${last.title}`.substring(0, 64);
                const out = last.content;
                console.log(`${task['bad_keyword']}`);

                let desp = `${last.title}\n${c.turndown(out)}\n${last.link}`;

                if (last.content && parseInt(task.translate) > 0 && process.env.OPENAI_KEY) {
                    const max_len = parseInt(process.env.TRANSLATE_MAX_LEN) > 10 ? parseInt(process.env.TRANSLATE_MAX_LEN) : 8000;
                    const ret0 = await translate(desp.substring(0, max_len));
                    if (ret0 && ret0.result) {
                        desp = `${ret0.result}\n\n\n\n---------\n\n\n\n${desp}`;
                    }
                }

                let ret = { "code": -1, "message": "Bad Key" };

                if (skey.toLowerCase().substring(0, 3) == "sct") {
                    ret = await sc_send(title, desp, short, String(skey).trim());
                } else if (skey.toLowerCase().substring(0, 4) == "http") {
                    const form = new FormData();
                    form.append('task_id', task['id']);
                    form.append('task_title', task['title']);
                    form.append('text', last.title);
                    form.append('title', last.title);
                    form.append('link', last.link);
                    form.append('desp', last.content);
                    try {
                        const response = await fetch(skey, {
                            method: 'POST',
                            body: form
                        });
                        ret = await response.json();
                    } catch (error) {
                        ret = { "code": 9, "message": "webhook " + error };
                    }
                } else if (skey.toLowerCase().substring(0, 12) == "apprise:raw ") {
                    const cmd = 'apprise ' + skey.substring(12) + ` -t "${title.replace(/"/g, '\\"')}" -b "${last.content.replace(/"/g, '\\"')}"`;
                    ret = { "code": 0, "message": "sent to apprise" };
                    const { exec } = require("child_process");
                    exec(cmd, (error, stdout, stderr) => {
                        if (error) {
                            console.log(`error: ${error.message}`);
                            return;
                        }
                        if (stderr) {
                            console.log(`stderr: ${stderr}`);
                            return;
                        }
                        console.log(`stdout: ${stdout}`);
                    });
                } else if (skey.toLowerCase().substring(0, 8) == "apprise ") {
                    const cmd = skey + ` -t "${title.replace(/"/g, '\\"')}" -b "${desp.replace(/"/g, '\\"')}"`;
                    ret = { "code": 0, "message": "sent to apprise" };
                    const { exec } = require("child_process");
                    exec(cmd, (error, stdout, stderr) => {
                        if (error) {
                            console.log(`error: ${error.message}`);
                            return;
                        }
                        if (stderr) {
                            console.log(`stderr: ${stderr}`);
                            return;
                        }
                        console.log(`stdout: ${stdout}`);
                    });
                }

                console.log(  "[INFO] 轮训中... 旧文章地址:" , old_content , "新文章地址:", last_content );

                sendResults.push({ skey, result: ret });
            }

            return { success: true, sendResults };

        } else {
            console.log("没有新内容", task.title);
            return { success: false, message: "没有新内容" };
        }
    } catch (error) {
        console.error("处理任务出错", task.title, error);
        return { success: false, error: error.message };
    }
}

async function translate( markdown )
{
    const llm = new Api2d( process.env.OPENAI_KEY, process.env.OPENAI_API_BASE );
    const prompt = `
# Task 请将Markdown清理掉样式和广告后翻译为中文

# RULES

1. 不要修改原始Markdown的格式，务必保留其中的图片、链接、视频等格式
1. 去掉输入内容中多余的CSS和HTML标签
1. 去掉原始内容中的广告和推广内容，比如购买会员、下载APP等
1. 专有名词保留，无需翻译

# INPUT

\`\`\`md    
${markdown}
\`\`\`


# OUTPUT

翻译结果：`;
    const prompt_long = `
# Task 请将Markdown清理掉样式和广告后翻译为中文，并输出120字的摘要

# RULES

## 摘要

1. 摘要长度120字以内
1. 主要回答两个问题：这些文字在说什么？为什么值得我看？

## 翻译

1. 不要修改原始Markdown的格式，务必保留其中的图片、链接、视频等格式
1. 去掉输入内容中多余的CSS和HTML标签
1. 去掉原始内容中的广告和推广内容，比如购买会员、下载APP等
1. 专有名词保留，无需翻译

# INPUT

\`\`\`md    
${markdown}
\`\`\`


# OUTPUT

格式如下：

# 摘要
(这里是摘要，如 本文...)

# 译文
(这里是翻译后的内容)

`;
    const ret = await llm.completion({
        model: markdown.length > 3000 ? 'gpt-3.5-turbo-16k' : 'gpt-3.5-turbo',
        messages:[
            {
                'role':'system',
                'content': '你是世界一流的翻译家，精通将各国语言翻译为中文。'
            },
            {
                'role':'user',
                // 'content': markdown.length > 1000 ? prompt_long :prompt
                'content': prompt
            },
        ],
        stream: true,
        onMessage: (string,char) => {
            // 不换行，仅输出一个字符
            process.stdout.write( char );
        },
    });
    console.log( "ret", ret );
    if( ret ) return {"result":ret};
    else return false;
}

async function sc_send( title, desp,short,  key )
{
    const url = String(key).startsWith('sctp') 
    ? `https://${key}.push.ft07.com/send`
    : `https://sctapi.ftqq.com/${key}.send`;
    const form = new FormData();
    form.append( 'text',title );
    form.append( 'desp',desp );
    form.append( 'short',short );
    try {
        const response = await fetch( url, {
            method: 'POST', 
            body: form
        } );

        const ret = await response.json();
        return ret;
    } catch (error) {
        console.log( error );
        return false;
    } 
}

module.exports = {
    processTask
};
