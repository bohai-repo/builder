RulePath = "/usr/local/openresty/nginx/conf/waf/wafconf/"
attacklog = "on"
logdir = "/etc/nginx/logs/"
UrlDeny="on"
Redirect="on"
CookieMatch="on"
postMatch="on" 
whiteModule="on" 
black_fileExt={"php","jsp"}
ipWhitelist={"127.0.0.1"}
ipBlocklist={"1.0.0.1"}
CCDeny="off"
CCrate="100/60"
html=[[
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>请求拦截</title>
    <style>
        body {
            font: 14px/1.5 "Microsoft Yahei", "宋体", sans-serif;
            color: #555;
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background-color: #f0f0f0;
        }

        .container {
            width: 80%;
            max-width: 1000px;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            border-radius: 8px;
            overflow: hidden;
        }

        .header {
            height: 40px;
            line-height: 40px;
            color: #fff;
            font-size: 16px;
            background: #6bb3f6;
            padding-left: 20px;
        }

        .content {
            border: 1px dashed #cdcece;
            border-top: none;
            font-size: 14px;
            padding: 20px;
            overflow-y: auto;
            background: #f3f7f9;
        }

        .content p {
            margin: 10px 0;
        }

        .content ul {
            list-style-type: none;
            padding-left: 20px;
        }

        .content li {
            margin: 5px 0;
        }

        .warning {
            font-weight: 600;
            color: #fc4f03;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">哎呀 你的请求被网站防火墙拦截了 :)</div>
        <div class="content">
            <p><span class="warning">您的请求带有不合法参数，已被网站管理员设置拦截！</span></p>
            <p>可能原因：您提交的内容包含危险的攻击请求</p>
            <p>如何解决：</p>
            <ul>
                <li>1）检查提交内容；</li>
                <li>2）如果您是正常的网站访客，请联系网站管理员: bohai@init.ac；</li>
            </ul>
        </div>
    </div>
</body>
</html>
]]
