import os

# 环境变量
CK_DATABASE = os.environ.get('CK_DATABASE')
CK_HOST = os.environ.get('CK_HOST')
CK_HTTP_PORT = os.environ.get('CK_HTTP_PORT')
CK_PASSWORD = os.environ.get('CK_PASSWORD')
CK_PORT = os.environ.get('CK_PORT')
CK_USER = os.environ.get('CK_USER')
MSG_TOKEN = os.environ.get('MSG_TOKEN')
MSG_TYPE = os.environ.get('MSG_TYPE')
PROM_K8S_TAG_KEY = os.environ.get('PROM_K8S_TAG_KEY')
DEFAULT_AT = os.environ.get('DEFAULT_AT')
ALERTMANAGER_EXTURL = os.environ.get('ALERTMANAGER_EXTURL')
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
