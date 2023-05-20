#!/bin/sh

trap 'rm -f "$token_cache_file" "$rules_cache_file"' EXIT
token_cache_file=$(mktemp) rules_cache_file=$(mktemp)|| exit 1

function request_token(){
	if [[ $appId == '' ]] && [[ $appSecretKey == '' ]]; then
		echo "[ERROR] Please check if env [appId] [appSecretKey] is configured.";exit 1
	fi
	/usr/bin/curl -s --connect-timeout ${request_timeout} --retry ${request_trynum} -c $token_cache_file -d "username=${appId}&password=${appSecretKey}" ${appurl}/?action=login &>/dev/null
	token=$(grep PHPSESSID ${token_cache_file}|awk '{print $7}')
}

function verify_ini(){
  key_name=$1
  key_cont=$(cat $rules_cache_file|grep -w "$key_name"|wc -l)
  if [[ $key_cont -le 0 ]];then
	echo -e "\033[31m$(date '+%Y/%m/%d %H:%M:%S') [E] Missing $key_name configuration\033[0m"
	exit 1
  fi
}

function extract_ini() {
  key_name=$1
  awk -F"=" "/${key_name}/ {print \$2}" "$rules_cache_file" | awk '{print $1}'
}

function request_rules(){
	request_token
	echo -e "$(date '+%Y/%m/%d %H:%M:%S') \033[33m[I] conf starting request  \033[0m"
	if [[ $appServerId == '' ]]; then echo "[ERROR] Please check if env [appServerId] is configured.";exit 1;fi
	curl -s --connect-timeout ${request_timeout} --retry ${request_trynum} "${appurl}/?page=panel&module=configuration&server=${appServerId}" -H 'cookie: PHPSESSID='"${token}"''|grep -Ev '<|{|}|:|;|All' > ${rules_cache_file}
	if [[ $? == 0 ]]; then
		verify_keys='common server_addr server_port protocol tls_enable user token admin_port admin_addr admin_user admin_pwd'
		for keys in $verify_keys;do
			verify_ini $keys
		done
		if [[ ! -f /app/frpc/frpc.ini  ]];then
			echo -e "$(date '+%Y/%m/%d %H:%M:%S') \033[33m[I] frpc startup \033[0m"
			cat $rules_cache_file > /app/frpc/frpc.ini
			return 0
		fi
		diff $rules_cache_file /app/frpc/frpc.ini &>/dev/null
		if [[ $? != 0 ]];then 
			cat $rules_cache_file > /app/frpc/frpc.ini
			echo -e "$(date '+%Y/%m/%d %H:%M:%S') \033[33m[I] conf has been get \033[0m"
		else
			echo -e "$(date '+%Y/%m/%d %H:%M:%S') \033[33m[I] conf no change. wait for ${exec_sec}s \033[0m"
			return 1
		fi
	else
		echo -e "$(date '+%Y/%m/%d %H:%M:%S') \033[31m[E] conf failed request\033[0m"
		return 1
	fi
}

function main(){
	request_rules
	if [[ $? != 0 ]];then return 1;fi
	procnum=$(ps -ef |grep frpc|grep -v grep|wc -l)
	if [[ $procnum -le 0 ]];then
		/app/frpc/frpc -c /app/frpc/frpc.ini &
	else
		curl -u "$(extract_ini admin_user):$(extract_ini admin_pwd)" http://127.0.0.1:$(extract_ini admin_port)/api/reload
		if [[ $? == 0 ]]; then
			echo -e "$(date '+%Y/%m/%d %H:%M:%S') \033[33m[I] conf success reload \033[0m"
		fi
	fi
}

while true; do
	main
	sleep $exec_sec
done
