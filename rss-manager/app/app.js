
const rssParser = require('rss-parser');
const express = require('express');
const path = require('path');
const fs = require('fs');
const { HttpsProxyAgent } = require('https-proxy-agent');
const { processTask } = require('./taskProcessor');
const app = express();

const cors = require('cors');
app.use(cors());

var multer = require('multer');
var forms = multer({limits: { fieldSize: 100 * 1024 * 1024 }});
const bodyParser = require('body-parser')
app.use(bodyParser.json());
app.use(forms.array()); 
app.use(bodyParser.urlencoded({ extended: true }));

// create data folder if not exists
if( !fs.existsSync( path.join(__dirname, 'data') ) ) fs.mkdirSync( path.join(__dirname, 'data') );

function checkApiKey (req, res, next) {
    
    if( process.env.ADMIN_KEY && process.env.ADMIN_KEY != ( req.query.key||req.body.key ))
    return res.json({"code":403,"message":"错误的ADMIN KEY"});
   
    next();
}

// add static files
app.use(express.static(path.join(__dirname, 'build')));

app.all("/check",checkApiKey,(req,res)=>{
    res.json({"info":"ok"});
});

app.post("/task/add",checkApiKey,async (req,res)=>{
    const { feed, keys, minutes, keyword, bad_keyword, translate } = req.body;
    if( !feed || !keys || !minutes ) return res.json({"code":400,"message":"参数错误"});

    let title = feed;
    let link = "";
    // 验证 feed ，并获取标题
    try {
        const parser = new rssParser({ timeout:100000 });
        const site = await parser.parseURL( feed );
        if( site.title ) title = site.title;
        if( site.link ) link = site.link;
        
        
    } catch (error) {
        res.json( {"error":"check feed error"} );
    }
    
    // read tasks.json
    const tasks =  fs.existsSync(path.join(__dirname,"data","tasks.json")) && JSON.parse( fs.readFileSync( path.join(__dirname,"data","tasks.json") ) ) || [] ;

    // gen uiniq id
    const id = Math.random().toString(36).substr(2, 9);
    
    // find exists feed and replace it
    const index = tasks.findIndex( item => item.feed == feed );
    if( index >= 0 ) tasks[index] = { id, title,feed,keys,minutes, keyword, bad_keyword, translate};
    else tasks.push( { id,title,link,feed,keys,minutes, keyword, bad_keyword, translate} );

    // unique array by feed
    const unique = [...new Map(tasks.map(item => [item.feed, item])).values()];
    // save tasks to tasks.json
    fs.writeFileSync( path.join(__dirname,"data","tasks.json"), JSON.stringify(unique) );

    res.json({"result":"ok"});

});

app.post("/task/modify",checkApiKey,async (req,res)=>{
    const { id, feed, keys, minutes, keyword, bad_keyword, translate } = req.body;
    if( !id || !feed || !keys || !minutes ) return res.json({"code":400,"message":"参数错误"});

    // read tasks.json
    const tasks =  fs.existsSync(path.join(__dirname,"data","tasks.json")) && JSON.parse( fs.readFileSync( path.join(__dirname,"data","tasks.json") ) ) || [] ;

    // find exists feed and replace it
    const index = tasks.findIndex( item => item.id == id );
    if( index >= 0 )
    {
        const old_title = tasks[index].title;
        const old_link = tasks[index].link||"";
        const old_last_time = tasks[index].last_time||"";
        const old_last_content = tasks[index].last_content||"";
        
        tasks[index] = { id, title:old_title,link:old_link,last_time:old_last_time,last_content:old_last_content,feed,keys,minutes, keyword, bad_keyword, translate};
    } 
    else {
        return res.json({"code":404,"message":"任务不存在"});
    }

    // unique array by feed
    const unique = [...new Map(tasks.map(item => [item.feed, item])).values()];
    // save tasks to tasks.json
    fs.writeFileSync( path.join(__dirname,"data","tasks.json"), JSON.stringify(unique) );

    res.json({"result":"ok"});

});

app.post("/task/remove",checkApiKey,async( req, res )=>{
    const tasks =  fs.existsSync(path.join(__dirname,"data","tasks.json")) && JSON.parse( fs.readFileSync( path.join(__dirname,"data","tasks.json") ) ) || [] ;

    // remove item from tasks by id
    const index = tasks.findIndex( item => item.id == req.body.id );
    if( index >= 0 ) tasks.splice(index,1);
    else return res.json({"code":404,"message":"任务不存在"});

    fs.writeFileSync( path.join(__dirname,"data","tasks.json"), JSON.stringify(tasks) );

    res.json({"result":"ok"});
});

app.post("/task/detail",checkApiKey,async( req, res )=>{
    const tasks =  fs.existsSync(path.join(__dirname,"data","tasks.json")) && JSON.parse( fs.readFileSync( path.join(__dirname,"data","tasks.json") ) ) || [] ;

    // find item by id
    const item = tasks.find( item => item.id == req.body.id );
    const ret = item ? {"result":item} : { "code":404, "message":"not found" };
    res.json( ret );
});

app.post("/task/list",checkApiKey,async( req, res )=>{
    const tasks =  fs.existsSync(path.join(__dirname,"data","tasks.json")) && JSON.parse( fs.readFileSync( path.join(__dirname,"data","tasks.json") ) ) || [] ;
    res.json( {"result":tasks} );
});

app.post("/task/test", checkApiKey, async (req, res) => {
    const { feed, keys, minutes, keyword, bad_keyword, translate } = req.body;
    if (!feed || !keys || !minutes) return res.json({ "code": 400, "message": "参数错误" });

    let title = feed;
    let link = "";

    // 验证 feed，并获取标题
    try {
        const parser = new rssParser({ timeout: 10000 });
        const site = await parser.parseURL(feed);
        if (site.title) title = site.title;
        if (site.link) link = site.link;
    } catch (error) {
        console.log(error);
        return res.json({ "error": "检查 feed 错误" });
    }

    // 生成唯一 ID
    const id = Math.random().toString(36).substr(2, 9);

    // 创建任务对象
    const task = { id, title, link, feed, keys, minutes, keyword, bad_keyword, translate };

    // 调用 processTask，测试模式下 isTest 为 true
    const result = await processTask(task, true);

    res.json({ "result": result });
});

app.get("/rss/base", async( req, res )=> res.json({"rss_base":process.env.RSS_BASE||"https://rsshub.app"}));

app.all("/rss/parse",checkApiKey,async (req,res)=>{
    const { url } = req.body;
    console.log( "url", url );
    try {
        let requestOptions = {};

        const httpProxy = process.env.HTTP_PROXY || process.env.http_proxy ;
        const httpsProxy = process.env.HTTPS_PROXY || process.env.https_proxy ;

        if (httpProxy) {
            requestOptions.agent = new HttpsProxyAgent(httpProxy);
        }else
        {
            if(httpsProxy) requestOptions.agent = new HttpsProxyAgent(httpsProxy);    
        }
        // console.log( "requestOptions", requestOptions.agent );
        const parser = new rssParser({ timeout:100000, requestOptions });
        const site = await parser.parseURL( url );
        const ret = site.items[0]||false;
        res.json( {"result":ret,"title":site.title} );
    } catch (error) {
        console.log( error );
        res.json( {"result":false} );
    }
    
    
});

app.get('*', function (request, response) {
    response.sendFile(path.resolve(__dirname, 'build' , 'index.html'));
});

app.use(function (err, req, res, next) {
    console.error(err);
    res.status(500).send('Internal Serverless Error');
  });
  
  app.listen(8000, () => {
    console.log(`start on http://localhost:8000`);
});