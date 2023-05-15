#!/bin/sh

trap 'rm -f "$token_cache_file" $rules_cache_file' EXIT
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

function request_rules(){
	request_token
	echo -e "\033[33m$(date '+%Y/%m/%d %H:%M:%S') [I] starting auto get conf \033[0m"
	if [[ $appServerId == '' ]]; then echo "[ERROR] Please check if env [appServerId] is configured.";exit 1;fi
	curl -s --connect-timeout ${request_timeout} --retry ${request_trynum} "${appurl}/?page=panel&module=configuration&server=${appServerId}" -H 'cookie: PHPSESSID='"${token}"''|grep -Ev '<|{|}|:|;|All' > ${rules_cache_file}
	if [[ $? == 0 ]]; then
		verify_keys='common server_addr server_port protocol tls_enable user token admin_port admin_addr admin_user admin_pwd'
		for keys in $verify_keys;do
			verify_ini $keys
		done
		if [[ ! -f /app/frpc/frpc.ini  ]];then
			echo -e "\033[33m$(date '+%Y/%m/%d %H:%M:%S') [I] first startup \033[0m"
			cat $rules_cache_file > /app/frpc/frpc.ini
			return 0
		fi
		diff $rules_cache_file /app/frpc/frpc.ini &>/dev/null
		if [[ $? != 0 ]];then 
			cat $rules_cache_file > /app/frpc/frpc.ini
			echo -e "\033[33m$(date '+%Y/%m/%d %H:%M:%S') [I] conf has been get \033[0m"
		else
			echo -e "\033[31m$(date '+%Y/%m/%d %H:%M:%S') [I] conf has been get  but config no change. wait for ${exec_sec} seconds and retrieve again \033[0m"
			return 1
		fi
	else
		echo -e "\033[31m$(date '+%Y/%m/%d %H:%M:%S') [E] conf Failed to get\033[0m"
		return 1
	fi
}

function main(){
	request_rules
	if [[ $? != 0 ]];then return 1;fi
	admin_pwd=$(cat $rules_cache_file|grep admin_pwd|sed 's/ //g')
    admin_port=$(cat $rules_cache_file|grep admin_port|sed 's/ //g')
    admin_user=$(cat $rules_cache_file|grep admin_user|sed 's/ //g')
	procnum=$(ps -ef |grep frpc|grep -v grep|wc -l)
	if [[ $procnum -le 0 ]];then
		/app/frpc/frpc -c /app/frpc/frpc.ini &
	else
		curl -u "${admin_user}:${admin_pwd}" http://127.0.0.1:${admin_port}/api/reload
		if [[ $? == 0 ]]; then
			echo -e "\033[33m$(date '+%Y/%m/%d %H:%M:%S') [I] success reload conf \033[0m"
		fi
	fi
}

while true; do
	main
	sleep $exec_sec
done