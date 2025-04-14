const fs = require("fs");
const path = require("path");
const dayjs = require("dayjs");
const rssParser = require('rss-parser');
const FormData = require('form-data');
const fetch = require('cross-fetch');
const turndown = require('turndown');

async function do_action()
{
    // read tasks from tasks.json
    let tasks = fs.existsSync(path.join(__dirname, "data", "tasks.json")) && JSON.parse(fs.readFileSync(path.join(__dirname, "data", "tasks.json"))) || [];

    let notify_items = [];

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

        const parser = new rssParser({ timeout:100000 });
        const feed = await parser.parseURL(tasks[index].feed);
        const last = feed.items[0];
        // console.log( "last", last );
        const last_content = last.guid||last.link;
        const old_content = tasks[index].last_content;
        tasks[index].last_time = dayjs().format("YYYY-MM-DD HH:mm:ss");
        tasks[index].last_content = last_content;

        

        console.log(  "[INFO] 轮训中... 旧文章地址:" , old_content , "新文章地址:", last_content );
        if( old_content &&  old_content != last_content )
        {
            // 如果设置了关键字，而文章标题不匹配关键字，那么跳过
            if( tasks[index]['keyword'] && last.title?.toLowerCase().indexOf(tasks[index]['keyword'].toLowerCase()) == -1 )
            {
                console.log("关键字不匹配，跳过", tasks[index]['keyword'] , last.title );
                continue;
            } 
            
            notify_items.push( {"current":tasks[index],"last":last} );
        }
    }

    // console.log( "new", tasks );

    // save task to tasks.json
    fs.writeFileSync( path.join(__dirname,"data","tasks.json"), JSON.stringify(tasks) );

    // 将通知移动到后边统一发送，避免因为发送失败导致内容没有保存
    // 循环通知
    for( const index in notify_items )
    {
        const item = notify_items[index];
        const current = item.current;
        const last = item.last;
        
        // 更新最新内容和时间
        const keys = current.keys.split("\n").map( item => item.trim() );
        // make keys array unique
        const unique_keys = [...new Set(keys)];
        for( const skey of unique_keys )
        {
            // send message to serverchan
            const c = new turndown();
            const title = `${current.title} 更新了`;
            const short = `${last.title}`.substring(0, 64);
            const desp = `${last.title}\n${c.turndown(last.content)}\n${last.link}`;

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
                    form.append( 'task_id',current['id'] );
                    form.append( 'task_title',current['title'] );
                    form.append( 'text',last.title );
                    form.append( 'title',last.title );
                    form.append( 'link',last.link );
                    form.append( 'desp',last.content );
                    console.log( form );
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
                            console.log(`stderr: ${stderr}`);
                            return;
                        }
                        console.log(`stdout: ${stdout}`);
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
                            console.log(`stderr: ${stderr}`);
                            return;
                        }
                        console.log(`stdout: ${stdout}`);
                    }
                    );   
                }
            }

            console.log( "send ret" , ret );
        }
    }
    


}

do_action();

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