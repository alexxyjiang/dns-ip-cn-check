#!/bin/sh
if [ -f cn.txt ]; then
    rm cn.txt
fi

curl https://raw.githubusercontent.com/Loyalsoldier/v2ray-rules-dat/release/direct-list.txt >> cn.txt
curl https://raw.githubusercontent.com/Loyalsoldier/v2ray-rules-dat/release/apple-cn.txt >> cn.txt
curl https://raw.githubusercontent.com/Loyalsoldier/v2ray-rules-dat/release/google-cn.txt >> cn.txt
sed '/^\(full\|regexp\)/!s/^/./g;s/^full://g;/^regexp:.*$/d;s/^/nameserver \//g;s/$/\/china/g;' -i cn.txt
cat cn.txt smartdns.cn.plus.rules | sort -u > cn.conf

echo "success; please copy cn.conf to /etc/smartdns/ and restart smartdns"
