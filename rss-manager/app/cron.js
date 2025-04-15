const fs = require("fs");
const path = require("path");
const dayjs = require("dayjs");
const rssParser = require('rss-parser');
const FormData = require('form-data');
const fetch = require('cross-fetch');
const turndown = require('turndown');
const Api2d = require('api2d');
const { HttpsProxyAgent } = require('https-proxy-agent');
// const { JSDOM } = require('jsdom');
// const Readability = require('@mozilla/readability').Readability;

async function do_action()
{
    // read tasks from tasks.json
    let tasks = fs.existsSync(path.join(__dirname, "data", "tasks.json")) && JSON.parse(fs.readFileSync(path.join(__dirname, "data", "tasks.json"))) || [];

    for( const index in tasks )
    {
        // console.log( "task", task );

        // 定时执行任务
        let  do_task = false;

        if(!tasks[index]?.last_time ) do_task = true;

        if(tasks[index].last_time && dayjs(tasks[index].last_time).add(tasks[index].minutes,'minutes').isBefore(dayjs()))
        {
            do_task = true;
        }

        if( !do_task ) continue;
        // if(   minutes % tasks[index].minutes != 0 ) continue;
        let requestOptions = {};

        const httpProxy = process.env.HTTP_PROXY || process.env.http_proxy ;
        const httpsProxy = process.env.HTTPS_PROXY || process.env.https_proxy ;

        if (httpProxy) {
            requestOptions.agent = new HttpsProxyAgent(httpProxy);
        }else
        {
            if(httpsProxy) requestOptions.agent = new HttpsProxyAgent(httpsProxy);    
        }

        const parser = new rssParser({ timeout:10000, requestOptions });
        const feed = await parser.parseURL(tasks[index].feed);
        const last = feed.items[0];
        // console.log( "last", last );
        const last_content = last.guid||last.link;
        const old_content = tasks[index].last_content;
        tasks[index].last_time = dayjs().format("YYYY-MM-DD HH:mm:ss");
        tasks[index].last_content = last_content;
        
        // 先保存一遍，这样就算发送通知失败了，也不会重复发送
        fs.writeFileSync(path.join(__dirname, "data", "tasks.json"), JSON.stringify(tasks));
        

        // console.log(  "OLD LAST" , old_content , last_content );
         console.log(  "[INFO] 轮训中... 旧文章地址:" , old_content , "新文章地址:", last_content );
        // console.log("[INFO] 轮训中... 共计 " + unique_keys.length + " 条任务，目前处理第" + (index + 1) + "个。旧文章地址:", old_content, "新文章地址:", last_content);
        if( old_content &&  old_content != last_content )
        {
//            console.log( "Feed唯一值有变动" );
            console.log(  "[INFO] "文章内容有更新:", last_content );
            // 如果白名单关键词检测，文章标题不匹配关键字，那么跳过
            const last_title = last.title?.toLowerCase();
            
            // 白名单，用 | 分隔关键词
            if( tasks[index]['keyword'])
            {
                const keywords = tasks[index]['keyword'].toLowerCase().split("|");
                let found = false;
                for( const keyword of keywords )
                {
                    if( last_title.indexOf(keyword) >= 0 ) found = true;
                }
                if( !found )
                {
                    console.log(`白名单跳过，${tasks[index]['keyword']}`);
                    continue;
                } 
            }

            // 黑名单
            if( tasks[index]['bad_keyword'])
            {
                const bad_keywords = tasks[index]['bad_keyword'].toLowerCase().split("|");
                let found = false;
                for( const bad_keyword of bad_keywords )
                {
                    if( last_title.indexOf(bad_keyword) >= 0 ) found = true;
                }
                if( found )
                {
                    console.log(`黑名单跳过，${tasks[index]['bad_keyword']}`);
                    continue;
                } 
            }
            
            
            // 更新最新内容和时间
            const keys = tasks[index].keys.split("\n").map( item => item.trim() );
            // make keys array unique
            const unique_keys = [...new Set(keys)];
            for( const skey of unique_keys )
            {
                // send message to serverchan
                const c = new turndown();
                const title = `${tasks[index].title} 更新了`;
                const short = `${last.title}`.substring(0, 64);

                // const html = last.content;
                // console.log( "html", html );
                // const dom = new JSDOM(html, {
                //     url: last.link,
                //     debug: true,
                // });
                // const reader = new Readability(dom.window.document);
                // const article = reader.parse();
                // console.log( "dom", JSON.stringify(dom.window.document) );
                // continue;
                // const out = article && article.content || html;
                const out = last.content;


                let desp = `${last.title}\n${c.turndown(out)}\n${last.link}`;

                // 如果 last.translate > 0 而且 last.content 不为空，而且环境变量包含 OPENAI_KEY  那么就翻译一下
                if( last.content && parseInt(tasks[index].translate) > 0 && process.env.OPENAI_KEY )
                {
                    const max_len = parseInt(process.env.TRANSLATE_MAX_LEN) > 10 ? parseInt(process.env.TRANSLATE_MAX_LEN) : 8000;
                    const ret0 = await translate( desp.substring(0,max_len) );
                    if( ret0 && ret0.result )
                    {
                        desp = `${ret0.result}\n\n\n\n---------\n\n\n\n${desp}`;
                    }
                }else
                {
                    // console.log( "last content", last.content, "translate", tasks[index].translate, "OPENAI_KEY", process.env.OPENAI_KEY );
                }

                let ret = {"code":-1,"message":"Bad Key"};
                // check skey( low case ) first 4 char is "sct"
                
                if( skey.toLowerCase().substring(0,3) == "sct" )
                {
                    ret = await sc_send( title, desp, short, String(skey).trim() );
                }else
                {
                    if( skey.toLowerCase().substring(0,4) == "http" )
                    {
                        const form = new FormData();
                        form.append( 'task_id',tasks[index]['id'] );
                        form.append( 'task_title',tasks[index]['title'] );
                        form.append( 'text',last.title );
                        form.append( 'title',last.title );
                        form.append( 'link',last.link );
                        form.append( 'desp',last.content );
                        /// console.log( form );
                        try {
                            const response = await fetch( skey, {
                                method: 'POST', 
                                body: form
                            } );
                            ret = await response.json();
                        } catch (error) {
                            ret = {"code":9,"message":"webhook "+error};
                        } 
                    }

                    if( skey.toLowerCase().substring(0,12) == "apprise:raw " )
                    {
                        // escape double quote in skey
                        
                        const cmd = 'apprise ' + skey.substring(12) + ` -t "${title.replace(/"/g, '\\"')}" -b "${last.content.replace(/"/g, '\\"')}"`;

                        ret = {"code":0,"message":"sent to apprise"};

                        // run cmd async 
                        const { exec } = require("child_process");
                        exec(cmd, (error, stdout, stderr) => {
                            if (error) {
                                console.log(`error: ${error.message}`);
                                return;
                            }
                            if (stderr) {
                                // console.log(`stderr: ${stderr}`);
                                return;
                            }
                            // console.log(`stdout: ${stdout}`);
                        }
                        );   
                    }

                    if( skey.toLowerCase().substring(0,8) == "apprise " )
                    {
                        const cmd = skey + ` -t "${title.replace(/"/g, '\\"')}" -b "${desp.replace(/"/g, '\\"')}"`;
                        ret = {"code":0,"message":"sent to apprise"};
                        // run cmd async 
                        const { exec } = require("child_process");
                        exec(cmd, (error, stdout, stderr) => {
                            if (error) {
                                console.log(`error: ${error.message}`);
                                return;
                            }
                            if (stderr) {
                                // console.log(`stderr: ${stderr}`);
                                return;
                            }
                            // console.log(`stdout: ${stdout}`);
                        }
                        );   
                    }
                }

                console.log( "[INFO] 推送信息结果" , ret );
            }
        }
    }

    // console.log( "new", tasks );

    // save task to tasks.json
    // 在循环内已经保存了，这里不需要再保存了
    // fs.writeFileSync( path.join(__dirname,"data","tasks.json"), JSON.stringify(tasks) );
}

do_action();

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
// 降运行端口打