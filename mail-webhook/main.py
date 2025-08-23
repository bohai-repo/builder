import smtplib
from email.mime.text import MIMEText
from flask import Flask, request

app = Flask(__name__)

# def verify_request(request):
#     api_key = 'admin'
#     expected_url = f'https://webhook-mail.init.ac/mail{api_key}'
#     if request.url != expected_url:
#         return False
#     if request.method != 'POST':
#         return False
#     if not request.is_json:
#         return False
#     payload = request.json
#     required_fields = ['to', 'subject', 'body']
#     if not all(field in payload for field in required_fields):
#         return False
#     return True

@app.route('/health', methods=['GET'])
def health():
    return '{"health":"true"}', 200

@app.route('/mail/', methods=['POST'])
def send_email():
    # if not verify_request(request):
    #     return '{"success":"false","message":"Unauthorized"}', 401

    payload = request.json

    to = payload['to']
    subject = payload['subject']
    body = payload['body']

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = "notify@init.ac"
    msg['To'] = to

    # 发送邮件
    smtp_server = 'smtp.exmail.qq.com'
    smtp_port = 465
    smtp_username = 'notify@init.ac'
    smtp_password = 'q464PnNYsYsS8HUa'
    smtp_conn = smtplib.SMTP_SSL(smtp_server, smtp_port)
    smtp_conn.login(smtp_username, smtp_password)
    smtp_conn.sendmail(smtp_username, [to], msg.as_string())
    smtp_conn.quit()

    return '{"success":"true","message":"Delivered"}', 200

if __name__ == '__main__':
    app.run("0.0.0.0","5600")